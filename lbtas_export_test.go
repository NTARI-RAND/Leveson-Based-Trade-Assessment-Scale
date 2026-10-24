//go:build darwin || linux

// Licensed under GNU Affero General Public License v3.0.
package main

import (
	"encoding/csv"
	"errors"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"reflect"
	"strconv"
	"syscall"
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

func TestCSVExportReportsDiskWriteFailure(t *testing.T) {
	if limitText := os.Getenv("LBTAS_TEST_FILE_LIMIT"); limitText != "" {
		runLimitedExport(t, limitText)
		return
	}
	// Isolate the process limit: it must never affect the parent test suite.
	for _, limit := range []string{"0", "4096"} {
		t.Run(limit, func(t *testing.T) {
			command := exec.Command(os.Args[0], "-test.run=^TestCSVExportReportsDiskWriteFailure$")
			command.Env = append(os.Environ(), "LBTAS_TEST_FILE_LIMIT="+limit)
			if output, err := command.CombinedOutput(); err != nil {
				t.Fatalf("limited export: %v\n%s", err, output)
			}
		})
	}
}

func runLimitedExport(t *testing.T, limitText string) {
	t.Helper()
	signal.Ignore(syscall.SIGXFSZ) // Return EFBIG instead of terminating the isolated process.
	limit, err := strconv.ParseUint(limitText, 10, 64)
	if err != nil {
		t.Fatal(err)
	}
	system := NewLevesonRatingSystem("", nil)
	if err := system.AddExchange("supplier"); err != nil {
		t.Fatal(err)
	}
	for i := 0; i < 1000; i++ {
		if err := system.AddRating("supplier", "reliability", 4); err != nil {
			t.Fatal(err)
		}
	}
	path := filepath.Join(t.TempDir(), "ratings.csv")
	var resource syscall.Rlimit
	if err := syscall.Getrlimit(syscall.RLIMIT_FSIZE, &resource); err != nil {
		t.Fatal(err)
	}
	resource.Cur = limit
	if err := syscall.Setrlimit(syscall.RLIMIT_FSIZE, &resource); err != nil {
		t.Fatal(err)
	}
	if err := system.ExportToCSV(path); !errors.Is(err, syscall.EFBIG) {
		t.Fatalf("CSV export error = %v, want file-too-large at %d bytes", err, limit)
	}
}
