/**
 * Leveson-Based Trade Assessment Scale (LBTAS)
 * 
 * A rating system for digital commerce based on Nancy Leveson's
 * aircraft software assessment methodology.
 * 
 * Copyright (C) 2024 Network Theory Applied Research Institute
 * Licensed under GNU Affero General Public License v3.0
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

import * as fs from 'fs';
import * as readline from 'readline';

const VERSION = '2.0.0';
const AUTHOR = 'Network Theory Applied Research Institute';
const LICENSE = 'AGPL-3.0';

interface ExchangeData {
  [category: string]: number[];
  _metadata: {
    created: string;
    total_ratings: number;
  };
}

interface StorageData {
  [exchange: string]: ExchangeData;
}

// A distribution is the count of ratings at each level, keyed by level string
// ("-1".."4"). Ratings are never averaged; this is the unit of reputation.
type Distribution = { [level: string]: number };

interface CategorySummary {
  distribution: Distribution;
  total: number;
}

interface RatingSummary {
  [category: string]: CategorySummary;
}

interface SystemReport {
  total_exchanges: number;
  total_ratings: number;
  overall_distribution: Distribution;
  category_distributions: { [category: string]: Distribution };
  exchange_distributions: { [exchange: string]: CategorySummary };
  // [exchange, -1 count] for exchanges with any -1, sorted by count descending.
  harm_flagged: Array<[string, number]>;
  generated_at: string;
}

// Display order for distributions: best (+4) to worst (-1).
const RATING_LEVELS = [4, 3, 2, 1, 0, -1];

// Short label for each rating level.
const RATING_LABELS: { [key: string]: string } = {
  '4': 'Delight',
  '3': 'No Negative Consequences',
  '2': 'Basic Satisfaction',
  '1': 'Basic Promise',
  '0': 'Cynical Satisfaction',
  '-1': 'No Trust',
};

function newDistribution(): Distribution {
  return { '-1': 0, '0': 0, '1': 0, '2': 0, '3': 0, '4': 0 };
}

function distributionOf(ratings: number[]): Distribution {
  const dist = newDistribution();
  for (const rating of ratings) {
    const key = String(rating);
    dist[key] = (dist[key] || 0) + 1;
  }
  return dist;
}

// Render a distribution best-to-worst, one line per level: level label : count.
function formatDistribution(dist: Distribution, indent: string = '  '): string {
  const lines: string[] = [];
  for (const level of RATING_LEVELS) {
    const sign = level > 0 ? `+${level}` : (level === 0 ? ' 0' : `${level}`);
    const label = RATING_LABELS[String(level)];
    lines.push(`${indent}${sign} ${label.padEnd(24)}: ${dist[String(level)]}`);
  }
  return lines.join('\n');
}

class LevesonRatingSystem {
  private readonly DEFAULT_CATEGORIES = ['reliability', 'usability', 'performance', 'support'];
  
  private readonly RATING_DESCRIPTIONS: { [key: number]: string } = {
    '-1': 'No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.',
    '0': 'Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.',
    '1': 'Basic Promise - Interaction meets all articulated user demands, no more.',
    '2': 'Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.',
    '3': 'No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.',
    '4': 'Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.'
  };

  private categories: string[];
  private storagePath: string | null;
  private exchanges: StorageData;

  constructor(storagePath: string | null = null, categories: string[] | null = null) {
    this.categories = categories || this.DEFAULT_CATEGORIES.slice();
    this.storagePath = storagePath;
    this.exchanges = {};

    if (this.storagePath) {
      this.loadFromFile();
    }
  }

  private loadFromFile(): void {
    if (!this.storagePath) return;
    
    try {
      if (fs.existsSync(this.storagePath)) {
        const data = fs.readFileSync(this.storagePath, 'utf8');
        this.exchanges = JSON.parse(data);
      }
    } catch (error) {
      console.error(`Error loading from file: ${error}`);
    }
  }

  private saveToFile(): void {
    if (!this.storagePath) return;
    
    try {
      fs.writeFileSync(this.storagePath, JSON.stringify(this.exchanges, null, 2));
    } catch (error) {
      console.error(`Error saving to file: ${error}`);
    }
  }

  addExchange(name: string): void {
    if (this.exchanges[name]) {
      throw new Error(`Exchange '${name}' already exists.`);
    }

    const exchangeData: ExchangeData = {
      _metadata: {
        created: new Date().toISOString(),
        total_ratings: 0
      }
    };

    for (const category of this.categories) {
      exchangeData[category] = [];
    }

    this.exchanges[name] = exchangeData;
    this.saveToFile();
  }

  addRating(exchangeName: string, criterion: string, rating: number): void {
    if (!this.exchanges[exchangeName]) {
      throw new Error(`Exchange '${exchangeName}' does not exist.`);
    }

    if (!this.categories.includes(criterion)) {
      throw new Error(`Criterion '${criterion}' not in valid categories: ${this.categories.join(', ')}`);
    }

    if (!Number.isInteger(rating) || rating < -1 || rating > 4) {
      throw new Error(`Rating must be integer between -1 and 4, got ${rating}`);
    }

    this.exchanges[exchangeName][criterion].push(rating);
    this.exchanges[exchangeName]._metadata.total_ratings++;
    this.saveToFile();
  }

  async getRating(criterion: string): Promise<number> {
    console.log(`\nRate ${criterion.charAt(0).toUpperCase() + criterion.slice(1)}:`);
    console.log('='.repeat(50));
    
    for (const [rating, description] of Object.entries(this.RATING_DESCRIPTIONS)) {
      console.log(`${rating.padStart(2)}: ${description}`);
    }
    
    console.log('='.repeat(50));

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise((resolve) => {
      const askRating = () => {
        rl.question(`Enter your rating for ${criterion.charAt(0).toUpperCase() + criterion.slice(1)} (-1 to 4): `, (answer) => {
          const rating = parseInt(answer);
          if (!isNaN(rating) && rating >= -1 && rating <= 4) {
            rl.close();
            resolve(rating);
          } else {
            console.log('Please enter a rating between -1 and 4.');
            askRating();
          }
        });
      };
      askRating();
    });
  }

  async rateExchange(name: string): Promise<void> {
    if (!this.exchanges[name]) {
      throw new Error(`Exchange '${name}' does not exist.`);
    }

    console.log(`\nRating '${name}' using Leveson-Based Trade Assessment Scale`);
    console.log('='.repeat(60));

    for (const criterion of this.categories) {
      const rating = await this.getRating(criterion);
      this.exchanges[name][criterion].push(rating);
      this.exchanges[name]._metadata.total_ratings++;
    }

    this.saveToFile();
    console.log(`\nRating completed for '${name}'!`);
  }

  viewRatings(name: string): RatingSummary {
    if (!this.exchanges[name]) {
      throw new Error(`Exchange '${name}' does not exist.`);
    }

    const summary: RatingSummary = {};

    for (const criterion of this.categories) {
      const ratings = this.exchanges[name][criterion];
      summary[criterion] = {
        distribution: distributionOf(ratings),
        total: ratings.length,
      };
    }

    return summary;
  }

  getAllExchanges(): string[] {
    return Object.keys(this.exchanges);
  }

  // The per-exchange "in service since" date stored at creation time.
  getCreated(name: string): string {
    const exchange = this.exchanges[name];
    return exchange && exchange._metadata ? exchange._metadata.created : 'unknown';
  }

  generateReport(): SystemReport {
    const totalExchanges = Object.keys(this.exchanges).length;

    if (totalExchanges === 0) {
      const categoryDistributions: { [category: string]: Distribution } = {};
      for (const category of this.categories) {
        categoryDistributions[category] = newDistribution();
      }
      return {
        total_exchanges: 0,
        total_ratings: 0,
        overall_distribution: newDistribution(),
        category_distributions: categoryDistributions,
        exchange_distributions: {},
        harm_flagged: [],
        generated_at: new Date().toISOString()
      };
    }

    const overall: number[] = [];
    const categoryTotals: { [key: string]: number[] } = {};
    const exchangeDistributions: { [exchange: string]: CategorySummary } = {};
    const harmFlagged: Array<[string, number]> = [];

    for (const category of this.categories) {
      categoryTotals[category] = [];
    }

    for (const [exchangeName, exchangeData] of Object.entries(this.exchanges)) {
      const exchangeRatings: number[] = [];

      for (const category of this.categories) {
        const ratings = exchangeData[category];
        for (const r of ratings) {
          categoryTotals[category].push(r);
          exchangeRatings.push(r);
          overall.push(r);
        }
      }

      const dist = distributionOf(exchangeRatings);
      exchangeDistributions[exchangeName] = {
        distribution: dist,
        total: exchangeRatings.length
      };
      if (dist['-1'] > 0) {
        harmFlagged.push([exchangeName, dist['-1']]);
      }
    }

    const categoryDistributions: { [category: string]: Distribution } = {};
    for (const category of this.categories) {
      categoryDistributions[category] = distributionOf(categoryTotals[category]);
    }

    // Sort harm-flagged by -1 count descending, then name ascending for stability.
    harmFlagged.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

    return {
      total_exchanges: totalExchanges,
      total_ratings: overall.length,
      overall_distribution: distributionOf(overall),
      category_distributions: categoryDistributions,
      exchange_distributions: exchangeDistributions,
      harm_flagged: harmFlagged,
      generated_at: new Date().toISOString()
    };
  }

  exportToJSON(outputPath: string): void {
    fs.writeFileSync(outputPath, JSON.stringify(this.exchanges, null, 2));
  }

  exportToCSV(outputPath: string): void {
    // Columns: exchange, category, rating, index (1-based position within the
    // category). No timestamp: the CLI store does not record per-rating times,
    // so a column of export-time stamps would be dishonest. Honest per-rating
    // timestamps live only in the API event records.
    const lines: string[] = ['exchange,category,rating,index'];

    for (const [exchangeName, exchangeData] of Object.entries(this.exchanges)) {
      for (const category of this.categories) {
        const ratings = exchangeData[category];
        for (let i = 0; i < ratings.length; i++) {
          lines.push(`${exchangeName},${category},${ratings[i]},${i + 1}`);
        }
      }
    }

    fs.writeFileSync(outputPath, lines.join('\n'));
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('LBTAS - Leveson-Based Trade Assessment Scale');
    console.log('\nUsage:');
    console.log('  node lbtas.js rate <exchange>');
    console.log('  node lbtas.js add <exchange> <criterion> <rating>');
    console.log('  node lbtas.js view <exchange>');
    console.log('  node lbtas.js list');
    console.log('  node lbtas.js report');
    console.log('  node lbtas.js export <format> <output>');
    return;
  }

  const command = args[0];
  const storage = 'lbtas_ratings.json';
  const system = new LevesonRatingSystem(storage);

  try {
    switch (command) {
      case 'rate': {
        const exchange = args[1];
        if (!exchange) {
          console.error('Error: Exchange name required');
          return;
        }
        if (!system.getAllExchanges().includes(exchange)) {
          system.addExchange(exchange);
        }
        await system.rateExchange(exchange);
        break;
      }

      case 'add': {
        const [, exchange, criterion, ratingStr] = args;
        if (!exchange || !criterion || !ratingStr) {
          console.error('Error: exchange, criterion, and rating required');
          return;
        }
        const rating = parseInt(ratingStr);
        if (!system.getAllExchanges().includes(exchange)) {
          system.addExchange(exchange);
        }
        system.addRating(exchange, criterion, rating);
        console.log(`Added rating ${rating} for ${criterion} to ${exchange}`);
        break;
      }

      case 'view': {
        const exchange = args[1];
        if (!exchange) {
          console.error('Error: Exchange name required');
          return;
        }
        const ratings = system.viewRatings(exchange);
        const exchangeTotal = Object.values(ratings).reduce((sum, block) => sum + block.total, 0);
        console.log(`\nRatings for '${exchange}':`);
        console.log('='.repeat(40));
        console.log(`In service since: ${system.getCreated(exchange)}`);
        console.log(`Total ratings (transaction volume): ${exchangeTotal}`);
        for (const [criterion, block] of Object.entries(ratings)) {
          const name = criterion.charAt(0).toUpperCase() + criterion.slice(1);
          console.log(`\n${name} (total: ${block.total}):`);
          console.log(formatDistribution(block.distribution));
        }
        break;
      }

      case 'list': {
        const exchanges = system.getAllExchanges();
        if (exchanges.length === 0) {
          console.log('No exchanges registered.');
        } else {
          console.log('Registered exchanges:');
          for (const exchange of exchanges) {
            const ratings = system.viewRatings(exchange);
            const total = Object.values(ratings).reduce((s, block) => s + block.total, 0);
            const harm = Object.values(ratings).reduce((s, block) => s + block.distribution['-1'], 0);
            let line = `  ${exchange} (${total} ratings)`;
            if (harm > 0) {
              line += `, ${harm}x -1 No Trust`;
            }
            console.log(line);
          }
        }
        break;
      }

      case 'report': {
        const report = system.generateReport();
        console.log('\nLBTAS System Report');
        console.log('='.repeat(50));
        console.log(`Total exchanges: ${report.total_exchanges}`);
        console.log(`Total ratings (transaction volume): ${report.total_ratings}`);

        console.log('\nOverall distribution:');
        console.log(formatDistribution(report.overall_distribution));

        console.log('\nCategory distributions:');
        for (const [category, dist] of Object.entries(report.category_distributions)) {
          const name = category.charAt(0).toUpperCase() + category.slice(1);
          console.log(`  ${name}:`);
          console.log(formatDistribution(dist, '    '));
        }

        if (Object.keys(report.exchange_distributions).length > 0) {
          console.log('\nPer-exchange distributions:');
          for (const [exchangeName, block] of Object.entries(report.exchange_distributions)) {
            console.log(`  ${exchangeName} (transaction volume: ${block.total}, in service since: ${system.getCreated(exchangeName)}):`);
            console.log(formatDistribution(block.distribution, '    '));
          }
        }

        if (report.harm_flagged.length > 0) {
          console.log('\nHarm-flagged exchanges (received -1 No Trust):');
          for (const [exchangeName, count] of report.harm_flagged) {
            console.log(`  ${exchangeName}: ${count}x -1`);
          }
        }
        break;
      }

      case 'export': {
        const format = args[1];
        const output = args[2];
        if (!format || !output) {
          console.error('Error: format and output path required');
          return;
        }
        if (format === 'json') {
          system.exportToJSON(output);
        } else if (format === 'csv') {
          system.exportToCSV(output);
        } else {
          console.error('Error: format must be json or csv');
          return;
        }
        console.log(`Exported to ${output}`);
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
    }
  } catch (error) {
    console.error(`Error: ${error}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { LevesonRatingSystem };
