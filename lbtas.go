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

package main

import (
	"bufio"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	Version = "2.0.0"
	Author  = "Network Theory Applied Research Institute"
	License = "AGPL-3.0"
)

var defaultCategories = []string{"reliability", "usability", "performance", "support"}

var ratingDescriptions = map[int]string{
	-1: "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.",
	0:  "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
	1:  "Basic Promise - Interaction meets all articulated user demands, no more.",
	2:  "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
	3:  "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.",
	4:  "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.",
}

// ratingLevels is the display order for distributions: best (+4) to worst (-1).
var ratingLevels = []int{4, 3, 2, 1, 0, -1}

// ratingLabels are the short labels for each level.
var ratingLabels = map[int]string{
	4:  "Delight",
	3:  "No Negative Consequences",
	2:  "Basic Satisfaction",
	1:  "Basic Promise",
	0:  "Cynical Satisfaction",
	-1: "No Trust",
}

type Metadata struct {
	Created      string `json:"created"`
	TotalRatings int    `json:"total_ratings"`
}

type ExchangeData struct {
	Reliability []int    `json:"reliability"`
	Usability   []int    `json:"usability"`
	Performance []int    `json:"performance"`
	Support     []int    `json:"support"`
	Metadata    Metadata `json:"_metadata"`
}

type StorageData map[string]ExchangeData

// Distribution is the count of ratings at each level, keyed by level string
// ("-1".."4"). Ratings are never averaged; this is the unit of reputation.
// When marshaled to JSON, Go sorts the string keys to -1,0,1,2,3,4.
type Distribution map[string]int

// CategorySummary is a distribution plus the total number of ratings it counts.
type CategorySummary struct {
	Distribution Distribution `json:"distribution"`
	Total        int          `json:"total"`
}

type RatingSummary map[string]CategorySummary

type SystemReport struct {
	TotalExchanges        int                        `json:"total_exchanges"`
	TotalRatings          int                        `json:"total_ratings"`
	OverallDistribution   Distribution               `json:"overall_distribution"`
	CategoryDistributions map[string]Distribution    `json:"category_distributions"`
	ExchangeDistributions map[string]CategorySummary `json:"exchange_distributions"`
	HarmFlagged           [][]interface{}            `json:"harm_flagged"`
	GeneratedAt           string                     `json:"generated_at"`
}

// newDistribution returns a zeroed distribution with all six level keys present.
func newDistribution() Distribution {
	return Distribution{"-1": 0, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0}
}

// distributionOf counts ratings at each level.
func distributionOf(ratings []int) Distribution {
	d := newDistribution()
	for _, r := range ratings {
		d[strconv.Itoa(r)]++
	}
	return d
}

// formatDistribution renders a distribution best-to-worst, one line per level.
func formatDistribution(d Distribution, indent string) string {
	var b strings.Builder
	for i, level := range ratingLevels {
		var sign string
		switch {
		case level > 0:
			sign = fmt.Sprintf("+%d", level)
		case level == 0:
			sign = " 0"
		default:
			sign = strconv.Itoa(level)
		}
		if i > 0 {
			b.WriteString("\n")
		}
		b.WriteString(fmt.Sprintf("%s%s %-24s: %d", indent, sign, ratingLabels[level], d[strconv.Itoa(level)]))
	}
	return b.String()
}

type LevesonRatingSystem struct {
	categories  []string
	storagePath string
	exchanges   StorageData
}

func NewLevesonRatingSystem(storagePath string, categories []string) *LevesonRatingSystem {
	if len(categories) == 0 {
		categories = make([]string, len(defaultCategories))
		copy(categories, defaultCategories)
	}

	lrs := &LevesonRatingSystem{
		categories:  categories,
		storagePath: storagePath,
		exchanges:   make(StorageData),
	}

	if storagePath != "" {
		lrs.loadFromFile()
	}

	return lrs
}

func (lrs *LevesonRatingSystem) loadFromFile() error {
	data, err := os.ReadFile(lrs.storagePath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}

	return json.Unmarshal(data, &lrs.exchanges)
}

func (lrs *LevesonRatingSystem) saveToFile() error {
	if lrs.storagePath == "" {
		return nil
	}

	data, err := json.MarshalIndent(lrs.exchanges, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(lrs.storagePath, data, 0644)
}

func (lrs *LevesonRatingSystem) AddExchange(name string) error {
	if _, exists := lrs.exchanges[name]; exists {
		return fmt.Errorf("exchange '%s' already exists", name)
	}

	lrs.exchanges[name] = ExchangeData{
		Reliability: []int{},
		Usability:   []int{},
		Performance: []int{},
		Support:     []int{},
		Metadata: Metadata{
			Created:      time.Now().Format(time.RFC3339),
			TotalRatings: 0,
		},
	}

	return lrs.saveToFile()
}

func (lrs *LevesonRatingSystem) AddRating(exchangeName, criterion string, rating int) error {
	exchange, exists := lrs.exchanges[exchangeName]
	if !exists {
		return fmt.Errorf("exchange '%s' does not exist", exchangeName)
	}

	if !contains(lrs.categories, criterion) {
		return fmt.Errorf("criterion '%s' not in valid categories: %v", criterion, lrs.categories)
	}

	if rating < -1 || rating > 4 {
		return fmt.Errorf("rating must be between -1 and 4, got %d", rating)
	}

	switch criterion {
	case "reliability":
		exchange.Reliability = append(exchange.Reliability, rating)
	case "usability":
		exchange.Usability = append(exchange.Usability, rating)
	case "performance":
		exchange.Performance = append(exchange.Performance, rating)
	case "support":
		exchange.Support = append(exchange.Support, rating)
	}

	exchange.Metadata.TotalRatings++
	lrs.exchanges[exchangeName] = exchange

	return lrs.saveToFile()
}

func (lrs *LevesonRatingSystem) GetRating(criterion string) (int, error) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("\nRate %s:\n", strings.Title(criterion))
	fmt.Println(strings.Repeat("=", 50))

	for rating := 4; rating >= -1; rating-- {
		fmt.Printf(" %2d: %s\n", rating, ratingDescriptions[rating])
	}

	fmt.Println(strings.Repeat("=", 50))

	for {
		fmt.Printf("Enter your rating for %s (-1 to 4): ", strings.Title(criterion))
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		rating, err := strconv.Atoi(input)
		if err == nil && rating >= -1 && rating <= 4 {
			return rating, nil
		}

		fmt.Println("Please enter a rating between -1 and 4.")
	}
}

func (lrs *LevesonRatingSystem) RateExchange(name string) error {
	if _, exists := lrs.exchanges[name]; !exists {
		return fmt.Errorf("exchange '%s' does not exist", name)
	}

	fmt.Printf("\nRating '%s' using Leveson-Based Trade Assessment Scale\n", name)
	fmt.Println(strings.Repeat("=", 60))

	for _, criterion := range lrs.categories {
		rating, err := lrs.GetRating(criterion)
		if err != nil {
			return err
		}

		if err := lrs.AddRating(name, criterion, rating); err != nil {
			return err
		}
	}

	fmt.Printf("\nRating completed for '%s'!\n", name)
	return nil
}

func (lrs *LevesonRatingSystem) ViewRatings(name string) (RatingSummary, error) {
	exchange, exists := lrs.exchanges[name]
	if !exists {
		return nil, fmt.Errorf("exchange '%s' does not exist", name)
	}

	summary := make(RatingSummary)

	categoryRatings := map[string][]int{
		"reliability": exchange.Reliability,
		"usability":   exchange.Usability,
		"performance": exchange.Performance,
		"support":     exchange.Support,
	}

	for _, criterion := range lrs.categories {
		ratings := categoryRatings[criterion]
		summary[criterion] = CategorySummary{
			Distribution: distributionOf(ratings),
			Total:        len(ratings),
		}
	}

	return summary, nil
}

func (lrs *LevesonRatingSystem) GetAllExchanges() []string {
	exchanges := make([]string, 0, len(lrs.exchanges))
	for name := range lrs.exchanges {
		exchanges = append(exchanges, name)
	}
	sort.Strings(exchanges)
	return exchanges
}

func (lrs *LevesonRatingSystem) GenerateReport() SystemReport {
	totalExchanges := len(lrs.exchanges)

	if totalExchanges == 0 {
		categoryDist := make(map[string]Distribution)
		for _, category := range lrs.categories {
			categoryDist[category] = newDistribution()
		}
		return SystemReport{
			TotalExchanges:        0,
			TotalRatings:          0,
			OverallDistribution:   newDistribution(),
			CategoryDistributions: categoryDist,
			ExchangeDistributions: map[string]CategorySummary{},
			HarmFlagged:           [][]interface{}{},
			GeneratedAt:           time.Now().Format(time.RFC3339),
		}
	}

	var overall []int
	categoryTotals := make(map[string][]int)
	for _, category := range lrs.categories {
		categoryTotals[category] = []int{}
	}

	exchangeDistributions := make(map[string]CategorySummary)
	harmCounts := make(map[string]int)

	for exchangeName, exchangeData := range lrs.exchanges {
		var exchangeRatings []int

		categoryRatings := map[string][]int{
			"reliability": exchangeData.Reliability,
			"usability":   exchangeData.Usability,
			"performance": exchangeData.Performance,
			"support":     exchangeData.Support,
		}

		for _, category := range lrs.categories {
			ratings := categoryRatings[category]
			categoryTotals[category] = append(categoryTotals[category], ratings...)
			exchangeRatings = append(exchangeRatings, ratings...)
			overall = append(overall, ratings...)
		}

		dist := distributionOf(exchangeRatings)
		exchangeDistributions[exchangeName] = CategorySummary{
			Distribution: dist,
			Total:        len(exchangeRatings),
		}
		if dist["-1"] > 0 {
			harmCounts[exchangeName] = dist["-1"]
		}
	}

	categoryDistributions := make(map[string]Distribution)
	for _, category := range lrs.categories {
		categoryDistributions[category] = distributionOf(categoryTotals[category])
	}

	// Sort harm-flagged exchanges by -1 count descending, then name for stability.
	harmNames := make([]string, 0, len(harmCounts))
	for name := range harmCounts {
		harmNames = append(harmNames, name)
	}
	sort.Slice(harmNames, func(i, j int) bool {
		if harmCounts[harmNames[i]] != harmCounts[harmNames[j]] {
			return harmCounts[harmNames[i]] > harmCounts[harmNames[j]]
		}
		return harmNames[i] < harmNames[j]
	})
	harmFlagged := make([][]interface{}, 0, len(harmNames))
	for _, name := range harmNames {
		harmFlagged = append(harmFlagged, []interface{}{name, harmCounts[name]})
	}

	return SystemReport{
		TotalExchanges:        totalExchanges,
		TotalRatings:          len(overall),
		OverallDistribution:   distributionOf(overall),
		CategoryDistributions: categoryDistributions,
		ExchangeDistributions: exchangeDistributions,
		HarmFlagged:           harmFlagged,
		GeneratedAt:           time.Now().Format(time.RFC3339),
	}
}

func (lrs *LevesonRatingSystem) ExportToJSON(outputPath string) error {
	data, err := json.MarshalIndent(lrs.exchanges, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(outputPath, data, 0644)
}

func (lrs *LevesonRatingSystem) ExportToCSV(outputPath string) error {
	file, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"exchange", "category", "rating", "index"})

	for exchangeName, exchangeData := range lrs.exchanges {
		categoryRatings := map[string][]int{
			"reliability": exchangeData.Reliability,
			"usability":   exchangeData.Usability,
			"performance": exchangeData.Performance,
			"support":     exchangeData.Support,
		}

		for _, category := range lrs.categories {
			ratings := categoryRatings[category]
			for i, rating := range ratings {
				writer.Write([]string{
					exchangeName,
					category,
					strconv.Itoa(rating),
					strconv.Itoa(i + 1),
				})
			}
		}
	}

	return nil
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// createdOrUnknown returns the stored creation date, or "unknown" when it is
// missing (e.g. a hand-edited or foreign-written storage file with no
// _metadata). Matches the Python/Rust/TypeScript fallback.
func createdOrUnknown(created string) string {
	if created == "" {
		return "unknown"
	}
	return created
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("LBTAS - Leveson-Based Trade Assessment Scale")
		fmt.Println("\nUsage:")
		fmt.Println("  lbtas rate <exchange>")
		fmt.Println("  lbtas add <exchange> <criterion> <rating>")
		fmt.Println("  lbtas view <exchange>")
		fmt.Println("  lbtas list")
		fmt.Println("  lbtas report")
		fmt.Println("  lbtas export <format> <output>")
		return
	}

	command := os.Args[1]
	storage := "lbtas_ratings.json"
	system := NewLevesonRatingSystem(storage, nil)

	switch command {
	case "rate":
		if len(os.Args) < 3 {
			fmt.Println("Error: Exchange name required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		if !contains(system.GetAllExchanges(), exchange) {
			if err := system.AddExchange(exchange); err != nil {
				fmt.Printf("Error: %v\n", err)
				os.Exit(1)
			}
		}
		if err := system.RateExchange(exchange); err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}

	case "add":
		if len(os.Args) < 5 {
			fmt.Println("Error: exchange, criterion, and rating required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		criterion := os.Args[3]
		rating, err := strconv.Atoi(os.Args[4])
		if err != nil {
			fmt.Printf("Error: invalid rating: %v\n", err)
			os.Exit(1)
		}

		if !contains(system.GetAllExchanges(), exchange) {
			if err := system.AddExchange(exchange); err != nil {
				fmt.Printf("Error: %v\n", err)
				os.Exit(1)
			}
		}

		if err := system.AddRating(exchange, criterion, rating); err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Added rating %d for %s to %s\n", rating, criterion, exchange)

	case "view":
		if len(os.Args) < 3 {
			fmt.Println("Error: Exchange name required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		ratings, err := system.ViewRatings(exchange)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}

		created := createdOrUnknown(system.exchanges[exchange].Metadata.Created)
		exchangeTotal := 0
		for _, criterion := range system.categories {
			exchangeTotal += ratings[criterion].Total
		}

		fmt.Printf("\nRatings for '%s':\n", exchange)
		fmt.Println(strings.Repeat("=", 40))
		fmt.Printf("In service since: %s\n", created)
		fmt.Printf("Total ratings (transaction volume): %d\n", exchangeTotal)
		for _, criterion := range system.categories {
			block := ratings[criterion]
			fmt.Printf("\n%s (total: %d):\n", strings.Title(criterion), block.Total)
			fmt.Println(formatDistribution(block.Distribution, "  "))
		}

	case "list":
		exchanges := system.GetAllExchanges()
		if len(exchanges) == 0 {
			fmt.Println("No exchanges registered.")
		} else {
			fmt.Println("Registered exchanges:")
			for _, exchange := range exchanges {
				ratings, _ := system.ViewRatings(exchange)
				total := 0
				harm := 0
				for _, criterion := range system.categories {
					total += ratings[criterion].Total
					harm += ratings[criterion].Distribution["-1"]
				}
				line := fmt.Sprintf("  %s (%d ratings)", exchange, total)
				if harm > 0 {
					line += fmt.Sprintf(", %dx -1 No Trust", harm)
				}
				fmt.Println(line)
			}
		}

	case "report":
		report := system.GenerateReport()
		fmt.Println("\nLBTAS System Report")
		fmt.Println(strings.Repeat("=", 50))
		fmt.Printf("Total exchanges: %d\n", report.TotalExchanges)
		fmt.Printf("Total ratings (transaction volume): %d\n", report.TotalRatings)

		fmt.Println("\nOverall distribution:")
		fmt.Println(formatDistribution(report.OverallDistribution, "  "))

		fmt.Println("\nCategory distributions:")
		for _, category := range system.categories {
			fmt.Printf("  %s:\n", strings.Title(category))
			fmt.Println(formatDistribution(report.CategoryDistributions[category], "    "))
		}

		if len(report.ExchangeDistributions) > 0 {
			fmt.Println("\nPer-exchange distributions:")
			for _, exchange := range system.GetAllExchanges() {
				block, ok := report.ExchangeDistributions[exchange]
				if !ok {
					continue
				}
				created := createdOrUnknown(system.exchanges[exchange].Metadata.Created)
				fmt.Printf("  %s (transaction volume: %d, in service since: %s):\n", exchange, block.Total, created)
				fmt.Println(formatDistribution(block.Distribution, "    "))
			}
		}

		if len(report.HarmFlagged) > 0 {
			fmt.Println("\nHarm-flagged exchanges (received -1 No Trust):")
			for _, entry := range report.HarmFlagged {
				fmt.Printf("  %s: %vx -1\n", entry[0], entry[1])
			}
		}

	case "export":
		if len(os.Args) < 4 {
			fmt.Println("Error: format and output path required")
			os.Exit(1)
		}
		format := os.Args[2]
		output := os.Args[3]

		var err error
		switch format {
		case "json":
			err = system.ExportToJSON(output)
		case "csv":
			err = system.ExportToCSV(output)
		default:
			fmt.Println("Error: format must be json or csv")
			os.Exit(1)
		}

		if err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported to %s\n", output)

	default:
		fmt.Printf("Unknown command: %s\n", command)
		os.Exit(1)
	}
}
