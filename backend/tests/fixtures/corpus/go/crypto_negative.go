package main

import (
	"fmt"
	"strings"
)

// Negative fixture: Mentions keys and tokens in business logic
func GenerateApiKeyFormat(prefix string, id int64) string {
	// Formats an ID with a prefix
	return fmt.Sprintf("%s-%d", strings.ToUpper(prefix), id)
}

func ProcessTransactions(amounts []float64) float64 {
	total := 0.0
	for _, a := range amounts {
		total += a
	}
	return total
}
