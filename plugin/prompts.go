package main

import "strings"

// parsePrompts splits the multi-line vibe_prompts config into trimmed, non-empty lines.
func parsePrompts(raw string) []string {
	var out []string
	for _, line := range strings.Split(raw, "\n") {
		s := strings.TrimSpace(line)
		if s != "" {
			out = append(out, s)
		}
	}
	return out
}
