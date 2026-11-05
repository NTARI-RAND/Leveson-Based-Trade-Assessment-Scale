//go:build darwin || linux

// Licensed under GNU Affero General Public License v3.0.
package main

import (
	"errors"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"regexp"
	"strconv"
	"syscall"
	"testing"
)

func TestCSVExportReportsDiskWriteFailure(t *testing.T) {
	if limitText := os.Getenv("LBTAS_TEST_FILE_LIMIT"); limitText != "" {
		runLimitedExport(t, limitText)
		return
	}
	// Isolate the process limit: it must never affect the parent test suite.
	testName := t.Name()
	for _, tc := range []struct{ name, limit, ratings string }{
		{"buffered-flush", "0", "1"},
		{"write-zero-limit", "0", "1000"},
		{"write-partial", "4096", "1000"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			command := exec.Command(os.Args[0], "-test.run=^"+regexp.QuoteMeta(testName)+"$")
			command.Env = append(os.Environ(), "LBTAS_TEST_FILE_LIMIT="+tc.limit, "LBTAS_TEST_RATING_COUNT="+tc.ratings)
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
	count, err := strconv.Atoi(os.Getenv("LBTAS_TEST_RATING_COUNT"))
	if err != nil {
		t.Fatal(err)
	}
	system := NewLevesonRatingSystem("", nil)
	if err := system.AddExchange("supplier"); err != nil {
		t.Fatal(err)
	}
	for i := 0; i < count; i++ {
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
