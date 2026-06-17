//go:build wasip1

package main

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/navidrome/navidrome/plugins/pdk/go/host"
	"github.com/navidrome/navidrome/plugins/pdk/go/metadata"
	"github.com/navidrome/navidrome/plugins/pdk/go/pdk"
)

// vibePlugin registers the plugin. It implements no metadata/similarity
// capability — it works purely via the lifecycle + scheduler exports below.
type vibePlugin struct{}

func main() {
	metadata.Register(&vibePlugin{})
}

//go:wasmexport nd_on_init
func onInit() int32 {
	pdk.Log(pdk.LogInfo, "Vibe Playlists plugin initializing...")
	schedule := configString("refresh_schedule", "0 5 * * *")
	_, err := host.SchedulerScheduleRecurring(schedule, "refresh-vibes", "refresh-vibes")
	if err != nil {
		pdk.Log(pdk.LogError, "Failed to schedule vibe refresh: "+err.Error())
	} else {
		pdk.Log(pdk.LogInfo, "Scheduled vibe refresh: "+schedule)
	}
	maybeRunInstant()
	pdk.Log(pdk.LogInfo, "Vibe Playlists plugin initialized")
	return 0
}

// maybeRunInstant generates a one-off playlist for the "Instant Vibe" config
// field. Saving the settings re-runs nd_on_init, so this is the closest thing
// to a "generate now" button the plugin API allows. A plugin can't clear its
// own config, so we dedup against the last value in KVStore: it fires only when
// the prompt actually changed, not on every restart/reload.
func maybeRunInstant() {
	prompt := strings.TrimSpace(configString("instant_vibe", ""))
	if prompt == "" {
		return
	}
	if last, ok, _ := host.KVStoreGet("last_instant_vibe"); ok && string(last) == prompt {
		return // unchanged since last run
	}
	if err := host.KVStoreSet("last_instant_vibe", []byte(prompt)); err != nil {
		pdk.Log(pdk.LogWarn, "Could not record instant vibe: "+err.Error())
	}
	pdk.Log(pdk.LogInfo, "Instant Vibe requested: "+prompt)
	err := generateVibe(configString("app_url", "http://vibe:4546"),
		configString("api_token", ""), prompt, configInt("tracks_per_playlist", 30))
	if err != nil {
		pdk.Log(pdk.LogError, "Instant Vibe failed: "+err.Error())
	} else {
		pdk.Log(pdk.LogInfo, "Instant Vibe submitted: "+prompt)
	}
}

// Navidrome requires the export name `nd_scheduler_callback` for the scheduler
// permission. We schedule a single recurring job, so we just refresh on any
// callback rather than dispatching on the payload.
//go:wasmexport nd_scheduler_callback
func ndSchedulerCallback() int32 {
	pdk.Log(pdk.LogInfo, "Scheduler callback fired; refreshing vibe playlists")
	return refreshVibes()
}

func refreshVibes() int32 {
	appURL := configString("app_url", "http://vibe:4546")
	apiToken := configString("api_token", "")
	count := configInt("tracks_per_playlist", 30)
	prompts := parsePrompts(configString("vibe_prompts", ""))
	if len(prompts) == 0 {
		pdk.Log(pdk.LogWarn, "No vibe_prompts configured; nothing to refresh")
		return 0
	}
	ok := 0
	for _, prompt := range prompts {
		if err := generateVibe(appURL, apiToken, prompt, count); err != nil {
			pdk.Log(pdk.LogError, "Vibe '"+prompt+"' failed: "+err.Error())
			continue
		}
		ok++
	}
	pdk.Log(pdk.LogInfo, fmt.Sprintf("Vibe refresh complete: %d/%d playlists created", ok, len(prompts)))
	return 0
}

func generateVibe(appURL, apiToken, prompt string, count int) error {
	// async:true -> the app returns 202 immediately and generates the playlist
	// in the background, so this call returns well within Navidrome's scheduler
	// callback deadline (~30s) instead of blocking on the slow LLM.
	reqBody, _ := json.Marshal(map[string]interface{}{"prompt": prompt, "count": count, "async": true})
	headers := map[string]string{"Content-Type": "application/json"}
	if apiToken != "" {
		headers["Authorization"] = "Bearer " + apiToken
	}
	resp, err := host.HTTPSend(host.HTTPRequest{
		URL:       appURL + "/api/vibe",
		Method:    "POST",
		Body:      reqBody,
		Headers:   headers,
		TimeoutMs: 15000,
	})
	if err != nil {
		return fmt.Errorf("HTTP request failed: %w", err)
	}
	if resp.StatusCode != 200 && resp.StatusCode != 202 {
		return fmt.Errorf("app returned status %d", resp.StatusCode)
	}
	return nil
}

func configString(key, defaultVal string) string {
	val, ok := host.ConfigGet(key)
	if !ok || val == "" {
		return defaultVal
	}
	return val
}

func configInt(key string, defaultVal int) int {
	val, ok := host.ConfigGetInt(key)
	if !ok {
		return defaultVal
	}
	return int(val)
}
