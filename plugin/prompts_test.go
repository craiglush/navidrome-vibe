package main

import "testing"

func TestParsePrompts(t *testing.T) {
	got := parsePrompts("  Lazy Sunday  \n\nRainy evening\n")
	if len(got) != 2 || got[0] != "Lazy Sunday" || got[1] != "Rainy evening" {
		t.Fatalf("unexpected: %#v", got)
	}
}

func TestParsePromptsEmpty(t *testing.T) {
	if len(parsePrompts("   \n  \n")) != 0 {
		t.Fatalf("expected no prompts")
	}
}
