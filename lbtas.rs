// Leveson-Based Trade Assessment Scale (LBTAS)
//
// A rating system for digital commerce based on Nancy Leveson's
// aircraft software assessment methodology.
//
// Copyright (C) 2024 Network Theory Applied Research Institute
// Licensed under GNU Affero General Public License v3.0
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

use std::collections::{BTreeMap, HashMap};
use std::fs;
use std::io::{self, Write};
use serde::{Deserialize, Serialize};
use chrono::Utc;

const VERSION: &str = "2.0.0";
const AUTHOR: &str = "Network Theory Applied Research Institute";
const LICENSE: &str = "AGPL-3.0";

const DEFAULT_CATEGORIES: &[&str] = &["reliability", "usability", "performance", "support"];

// Display order for distributions: best (+4) to worst (-1).
const RATING_LEVELS: [i8; 6] = [4, 3, 2, 1, 0, -1];

// Short label for each rating level.
fn rating_label(level: i8) -> &'static str {
    match level {
        4 => "Delight",
        3 => "No Negative Consequences",
        2 => "Basic Satisfaction",
        1 => "Basic Promise",
        0 => "Cynical Satisfaction",
        -1 => "No Trust",
        _ => "",
    }
}

// Capitalize the first character of a string for display.
fn capitalize(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        Some(c) => c.to_uppercase().collect::<String>() + chars.as_str(),
        None => String::new(),
    }
}

// A distribution is the count of ratings at each level, keyed by level string
// ("-1".."4"). Ratings are never averaged; this is the unit of reputation. A
// BTreeMap keeps the keys in a stable serialized order (-1,0,1,2,3,4).
type Distribution = BTreeMap<String, u64>;

fn new_distribution() -> Distribution {
    let mut dist = BTreeMap::new();
    for level in ["-1", "0", "1", "2", "3", "4"] {
        dist.insert(level.to_string(), 0u64);
    }
    dist
}

fn distribution_of(ratings: &[i8]) -> Distribution {
    let mut dist = new_distribution();
    for &rating in ratings {
        *dist.entry(rating.to_string()).or_insert(0) += 1;
    }
    dist
}

// Render a distribution best-to-worst, one line per level: level label : count.
fn format_distribution(dist: &Distribution, indent: &str) -> String {
    let mut lines = Vec::new();
    for &level in RATING_LEVELS.iter() {
        let sign = if level > 0 {
            format!("+{}", level)
        } else if level == 0 {
            " 0".to_string()
        } else {
            level.to_string()
        };
        let count = dist.get(&level.to_string()).copied().unwrap_or(0);
        lines.push(format!("{}{} {:<24}: {}", indent, sign, rating_label(level), count));
    }
    lines.join("\n")
}

fn rating_descriptions() -> HashMap<i8, &'static str> {
    let mut map = HashMap::new();
    map.insert(-1, "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.");
    map.insert(0, "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.");
    map.insert(1, "Basic Promise - Interaction meets all articulated user demands, no more.");
    map.insert(2, "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.");
    map.insert(3, "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.");
    map.insert(4, "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.");
    map
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Metadata {
    created: String,
    total_ratings: usize,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ExchangeData {
    reliability: Vec<i8>,
    usability: Vec<i8>,
    performance: Vec<i8>,
    support: Vec<i8>,
    #[serde(rename = "_metadata")]
    metadata: Metadata,
}

impl ExchangeData {
    fn new() -> Self {
        ExchangeData {
            reliability: Vec::new(),
            usability: Vec::new(),
            performance: Vec::new(),
            support: Vec::new(),
            metadata: Metadata {
                created: Utc::now().to_rfc3339(),
                total_ratings: 0,
            },
        }
    }

    fn get_category_mut(&mut self, category: &str) -> Option<&mut Vec<i8>> {
        match category {
            "reliability" => Some(&mut self.reliability),
            "usability" => Some(&mut self.usability),
            "performance" => Some(&mut self.performance),
            "support" => Some(&mut self.support),
            _ => None,
        }
    }

    fn get_category(&self, category: &str) -> Option<&Vec<i8>> {
        match category {
            "reliability" => Some(&self.reliability),
            "usability" => Some(&self.usability),
            "performance" => Some(&self.performance),
            "support" => Some(&self.support),
            _ => None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct StorageData {
    #[serde(flatten)]
    exchanges: HashMap<String, ExchangeData>,
}

// A category's rating distribution plus the total it counts.
#[derive(Debug, Serialize)]
struct CategorySummary {
    distribution: Distribution,
    total: u64,
}

#[derive(Debug)]
struct RatingSummary {
    ratings: BTreeMap<String, CategorySummary>,
}

#[derive(Debug, Serialize)]
struct SystemReport {
    total_exchanges: usize,
    total_ratings: usize,
    overall_distribution: Distribution,
    category_distributions: BTreeMap<String, Distribution>,
    exchange_distributions: BTreeMap<String, CategorySummary>,
    // List of [exchange, -1 count] for exchanges with any -1, by count descending.
    harm_flagged: Vec<(String, u64)>,
    generated_at: String,
}

struct LevesonRatingSystem {
    categories: Vec<String>,
    storage_path: Option<String>,
    exchanges: HashMap<String, ExchangeData>,
}

impl LevesonRatingSystem {
    fn new(storage_path: Option<String>, categories: Option<Vec<String>>) -> Self {
        let categories = categories.unwrap_or_else(|| {
            DEFAULT_CATEGORIES.iter().map(|s| s.to_string()).collect()
        });

        let mut system = LevesonRatingSystem {
            categories,
            storage_path,
            exchanges: HashMap::new(),
        };

        if system.storage_path.is_some() {
            let _ = system.load_from_file();
        }

        system
    }

    fn load_from_file(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(path) = &self.storage_path {
            if std::path::Path::new(path).exists() {
                let data = fs::read_to_string(path)?;
                let storage: StorageData = serde_json::from_str(&data)?;
                self.exchanges = storage.exchanges;
            }
        }
        Ok(())
    }

    fn save_to_file(&self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(path) = &self.storage_path {
            let storage = StorageData {
                exchanges: self.exchanges.clone(),
            };
            let data = serde_json::to_string_pretty(&storage)?;
            fs::write(path, data)?;
        }
        Ok(())
    }

    fn add_exchange(&mut self, name: &str) -> Result<(), String> {
        if self.exchanges.contains_key(name) {
            return Err(format!("Exchange '{}' already exists", name));
        }

        self.exchanges.insert(name.to_string(), ExchangeData::new());
        self.save_to_file().map_err(|e| e.to_string())?;
        Ok(())
    }

    fn add_rating(&mut self, exchange_name: &str, criterion: &str, rating: i8) -> Result<(), String> {
        let exchange = self.exchanges.get_mut(exchange_name)
            .ok_or_else(|| format!("Exchange '{}' does not exist", exchange_name))?;

        if !self.categories.contains(&criterion.to_string()) {
            return Err(format!("Criterion '{}' not in valid categories: {:?}", criterion, self.categories));
        }

        if rating < -1 || rating > 4 {
            return Err(format!("Rating must be between -1 and 4, got {}", rating));
        }

        if let Some(category) = exchange.get_category_mut(criterion) {
            category.push(rating);
            exchange.metadata.total_ratings += 1;
            self.save_to_file().map_err(|e| e.to_string())?;
            Ok(())
        } else {
            Err(format!("Invalid category: {}", criterion))
        }
    }

    fn get_rating(&self, criterion: &str) -> Result<i8, Box<dyn std::error::Error>> {
        let descriptions = rating_descriptions();

        println!("\nRate {}:", criterion.chars().next().unwrap().to_uppercase().collect::<String>() + &criterion[1..]);
        println!("{}", "=".repeat(50));

        for rating in ((-1)..=4).rev() {
            println!(" {:2}: {}", rating, descriptions.get(&rating).unwrap());
        }

        println!("{}", "=".repeat(50));

        loop {
            print!("Enter your rating for {} (-1 to 4): ", criterion.chars().next().unwrap().to_uppercase().collect::<String>() + &criterion[1..]);
            io::stdout().flush()?;

            let mut input = String::new();
            io::stdin().read_line(&mut input)?;

            if let Ok(rating) = input.trim().parse::<i8>() {
                if rating >= -1 && rating <= 4 {
                    return Ok(rating);
                }
            }

            println!("Please enter a rating between -1 and 4.");
        }
    }

    fn rate_exchange(&mut self, name: &str) -> Result<(), Box<dyn std::error::Error>> {
        if !self.exchanges.contains_key(name) {
            return Err(format!("Exchange '{}' does not exist", name).into());
        }

        println!("\nRating '{}' using Leveson-Based Trade Assessment Scale", name);
        println!("{}", "=".repeat(60));

        for criterion in self.categories.clone() {
            let rating = self.get_rating(&criterion)?;
            self.add_rating(name, &criterion, rating)?;
        }

        println!("\nRating completed for '{}'!", name);
        Ok(())
    }

    fn view_ratings(&self, name: &str) -> Result<RatingSummary, String> {
        let exchange = self.exchanges.get(name)
            .ok_or_else(|| format!("Exchange '{}' does not exist", name))?;

        let mut ratings = BTreeMap::new();

        for criterion in &self.categories {
            if let Some(category) = exchange.get_category(criterion) {
                ratings.insert(criterion.clone(), CategorySummary {
                    distribution: distribution_of(category),
                    total: category.len() as u64,
                });
            }
        }

        Ok(RatingSummary { ratings })
    }

    fn get_all_exchanges(&self) -> Vec<String> {
        let mut exchanges: Vec<String> = self.exchanges.keys().cloned().collect();
        exchanges.sort();
        exchanges
    }

    fn generate_report(&self) -> SystemReport {
        if self.exchanges.is_empty() {
            let mut category_distributions = BTreeMap::new();
            for category in &self.categories {
                category_distributions.insert(category.clone(), new_distribution());
            }
            return SystemReport {
                total_exchanges: 0,
                total_ratings: 0,
                overall_distribution: new_distribution(),
                category_distributions,
                exchange_distributions: BTreeMap::new(),
                harm_flagged: Vec::new(),
                generated_at: Utc::now().to_rfc3339(),
            };
        }

        let mut overall: Vec<i8> = Vec::new();
        let mut category_totals: BTreeMap<String, Vec<i8>> = BTreeMap::new();
        for category in &self.categories {
            category_totals.insert(category.clone(), Vec::new());
        }

        let mut exchange_distributions: BTreeMap<String, CategorySummary> = BTreeMap::new();
        let mut harm_flagged: Vec<(String, u64)> = Vec::new();

        for (exchange_name, exchange_data) in &self.exchanges {
            let mut exchange_ratings: Vec<i8> = Vec::new();

            for category in &self.categories {
                if let Some(ratings) = exchange_data.get_category(category) {
                    category_totals.get_mut(category).unwrap().extend(ratings);
                    exchange_ratings.extend(ratings);
                    overall.extend(ratings);
                }
            }

            let dist = distribution_of(&exchange_ratings);
            let minus_one = dist.get("-1").copied().unwrap_or(0);
            if minus_one > 0 {
                harm_flagged.push((exchange_name.clone(), minus_one));
            }
            exchange_distributions.insert(exchange_name.clone(), CategorySummary {
                distribution: dist,
                total: exchange_ratings.len() as u64,
            });
        }

        let mut category_distributions: BTreeMap<String, Distribution> = BTreeMap::new();
        for category in &self.categories {
            category_distributions.insert(category.clone(), distribution_of(&category_totals[category]));
        }

        // Sort harm-flagged by -1 count descending, then name ascending for stability.
        harm_flagged.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));

        SystemReport {
            total_exchanges: self.exchanges.len(),
            total_ratings: overall.len(),
            overall_distribution: distribution_of(&overall),
            category_distributions,
            exchange_distributions,
            harm_flagged,
            generated_at: Utc::now().to_rfc3339(),
        }
    }

    fn export_to_json(&self, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let storage = StorageData {
            exchanges: self.exchanges.clone(),
        };
        let data = serde_json::to_string_pretty(&storage)?;
        fs::write(output_path, data)?;
        Ok(())
    }

    fn export_to_csv(&self, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut wtr = csv::Writer::from_path(output_path)?;
        wtr.write_record(&["exchange", "category", "rating", "index"])?;

        for (exchange_name, exchange_data) in &self.exchanges {
            for category in &self.categories {
                if let Some(ratings) = exchange_data.get_category(category) {
                    for (i, &rating) in ratings.iter().enumerate() {
                        wtr.write_record(&[
                            exchange_name,
                            category,
                            &rating.to_string(),
                            &(i + 1).to_string(),
                        ])?;
                    }
                }
            }
        }

        wtr.flush()?;
        Ok(())
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        println!("LBTAS - Leveson-Based Trade Assessment Scale");
        println!("\nUsage:");
        println!("  lbtas rate <exchange>");
        println!("  lbtas add <exchange> <criterion> <rating>");
        println!("  lbtas view <exchange>");
        println!("  lbtas list");
        println!("  lbtas report");
        println!("  lbtas export <format> <output>");
        return;
    }

    let command = &args[1];
    let storage = "lbtas_ratings.json".to_string();
    let mut system = LevesonRatingSystem::new(Some(storage), None);

    match command.as_str() {
        "rate" => {
            if args.len() < 3 {
                eprintln!("Error: Exchange name required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            if !system.get_all_exchanges().contains(exchange) {
                if let Err(e) = system.add_exchange(exchange) {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }
            if let Err(e) = system.rate_exchange(exchange) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }

        "add" => {
            if args.len() < 5 {
                eprintln!("Error: exchange, criterion, and rating required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            let criterion = &args[3];
            let rating: i8 = match args[4].parse() {
                Ok(r) => r,
                Err(_) => {
                    eprintln!("Error: invalid rating");
                    std::process::exit(1);
                }
            };

            if !system.get_all_exchanges().contains(exchange) {
                if let Err(e) = system.add_exchange(exchange) {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }

            if let Err(e) = system.add_rating(exchange, criterion, rating) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
            println!("Added rating {} for {} to {}", rating, criterion, exchange);
        }

        "view" => {
            if args.len() < 3 {
                eprintln!("Error: Exchange name required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            match system.view_ratings(exchange) {
                Ok(summary) => {
                    let created = system.exchanges.get(exchange)
                        .map(|e| e.metadata.created.clone())
                        .unwrap_or_else(|| "unknown".to_string());
                    let exchange_total: u64 = summary.ratings.values().map(|b| b.total).sum();
                    println!("\nRatings for '{}':", exchange);
                    println!("{}", "=".repeat(40));
                    println!("In service since: {}", created);
                    println!("Total ratings (transaction volume): {}", exchange_total);
                    for category in &system.categories {
                        if let Some(block) = summary.ratings.get(category) {
                            println!("\n{} (total: {}):", capitalize(category), block.total);
                            println!("{}", format_distribution(&block.distribution, "  "));
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }
        }

        "list" => {
            let exchanges = system.get_all_exchanges();
            if exchanges.is_empty() {
                println!("No exchanges registered.");
            } else {
                println!("Registered exchanges:");
                for exchange in exchanges {
                    if let Ok(summary) = system.view_ratings(&exchange) {
                        let total: u64 = summary.ratings.values().map(|b| b.total).sum();
                        let harm: u64 = summary.ratings.values()
                            .map(|b| b.distribution.get("-1").copied().unwrap_or(0))
                            .sum();
                        let mut line = format!("  {} ({} ratings)", exchange, total);
                        if harm > 0 {
                            line.push_str(&format!(", {}x -1 No Trust", harm));
                        }
                        println!("{}", line);
                    }
                }
            }
        }

        "report" => {
            let report = system.generate_report();
            println!("\nLBTAS System Report");
            println!("{}", "=".repeat(50));
            println!("Total exchanges: {}", report.total_exchanges);
            println!("Total ratings (transaction volume): {}", report.total_ratings);

            println!("\nOverall distribution:");
            println!("{}", format_distribution(&report.overall_distribution, "  "));

            println!("\nCategory distributions:");
            for category in &system.categories {
                if let Some(dist) = report.category_distributions.get(category) {
                    println!("  {}:", capitalize(category));
                    println!("{}", format_distribution(dist, "    "));
                }
            }

            if !report.exchange_distributions.is_empty() {
                println!("\nPer-exchange distributions:");
                for exchange in system.get_all_exchanges() {
                    if let Some(block) = report.exchange_distributions.get(&exchange) {
                        let created = system.exchanges.get(&exchange)
                            .map(|e| e.metadata.created.clone())
                            .unwrap_or_else(|| "unknown".to_string());
                        println!("  {} (transaction volume: {}, in service since: {}):", exchange, block.total, created);
                        println!("{}", format_distribution(&block.distribution, "    "));
                    }
                }
            }

            if !report.harm_flagged.is_empty() {
                println!("\nHarm-flagged exchanges (received -1 No Trust):");
                for (exchange, count) in &report.harm_flagged {
                    println!("  {}: {}x -1", exchange, count);
                }
            }
        }

        "export" => {
            if args.len() < 4 {
                eprintln!("Error: format and output path required");
                std::process::exit(1);
            }
            let format = &args[2];
            let output = &args[3];

            let result = match format.as_str() {
                "json" => system.export_to_json(output),
                "csv" => system.export_to_csv(output),
                _ => {
                    eprintln!("Error: format must be json or csv");
                    std::process::exit(1);
                }
            };

            if let Err(e) = result {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
            println!("Exported to {}", output);
        }

        _ => {
            eprintln!("Unknown command: {}", command);
            std::process::exit(1);
        }
    }
}
