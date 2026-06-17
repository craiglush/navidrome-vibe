//go:build wasip1

package main

import (
	"encoding/json"
	"fmt"

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
	pdk.Log(pdk.LogInfo, "Vibe Playlists plugin initialized")
	return 0
}

//go:wasmexport nd_on_schedule
func onSchedule() int32 {
	payload := string(pdk.Input())
	pdk.Log(pdk.LogInfo, "Scheduled task triggered: "+payload)
	switch payload {
	case "refresh-vibes":
		return refreshVibes()
	default:
		pdk.Log(pdk.LogWarn, "Unknown schedule payload: "+payload)
		return 0
	}
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
	reqBody, _ := json.Marshal(map[string]interface{}{"prompt": prompt, "count": count})
	headers := map[string]string{"Content-Type": "application/json"}
	if apiToken != "" {
		headers["Authorization"] = "Bearer " + apiToken
	}
	resp, err := host.HTTPSend(host.HTTPRequest{
		URL:       appURL + "/api/vibe",
		Method:    "POST",
		Body:      reqBody,
		Headers:   headers,
		TimeoutMs: 180000,
	})
	if err != nil {
		return fmt.Errorf("HTTP request failed: %w", err)
	}
	if resp.StatusCode != 200 {
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
