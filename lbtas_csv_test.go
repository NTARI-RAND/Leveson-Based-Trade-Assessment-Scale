// Licensed under GNU Affero General Public License v3.0.
package main

import (
	"encoding/csv"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestCSVExportPreservesFields(t *testing.T) {
	const exchangeName = "supplier, quoted"
	system := NewLevesonRatingSystem("", nil)
	if err := system.AddExchange(exchangeName); err != nil {
		t.Fatal(err)
	}
	for _, rating := range []int{-1, 4} {
		if err := system.AddRating(exchangeName, "reliability", rating); err != nil {
			t.Fatal(err)
		}
	}
	path := filepath.Join(t.TempDir(), "ratings.csv")
	if err := system.ExportToCSV(path); err != nil {
		t.Fatal(err)
	}
	file, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = file.Close() }()
	rows, err := csv.NewReader(file).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	want := [][]string{
		{"exchange", "category", "rating", "index"},
		{exchangeName, "reliability", "-1", "1"},
		{exchangeName, "reliability", "4", "2"},
	}
	if !reflect.DeepEqual(rows, want) {
		t.Fatalf("CSV rows = %v, want %v", rows, want)
	}
}
