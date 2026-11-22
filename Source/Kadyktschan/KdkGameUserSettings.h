// Player settings saved in GameUserSettings.ini: the engine's scalability groups plus the options the
// settings menu adds on top (mouse, hardware ray tracing, Nanite, FPS counter).

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "Scalability.h"
#include "KdkGameUserSettings.generated.h"

UCLASS(config = GameUserSettings, configdonotcheckdefaults)
class KADYKTSCHAN_API UKdkGameUserSettings : public UGameUserSettings
{
	GENERATED_BODY()

public:
	/** The active settings object (GameUserSettingsClassName in DefaultEngine.ini points here). */
	static UKdkGameUserSettings* Get();

	/** Lowest render resolution the menu offers, in percent. */
	static constexpr float MinRenderScale = 25.f;

	virtual void SetToDefaults() override;
	/** Also pushes the extra options below into their console variables. */
	virtual void ApplyNonResolutionSettings() override;

	/** Writes the player's own quality levels even while the shooter mode has lowered them for the frame rate
	 *  (the engine saves the live levels, also on quit: 2026-11-11 a test run saved shadows 1 / foliage 2). */
	virtual void SaveSettings() override;

	/** Set by the shooter mode's dynamic graphics while a lowered level is active; unset at level 0. */
	TOptional<Scalability::FQualityLevels> TemporaryQualityOverride;

	/** Multiplier on mouse/stick look input. */
	UPROPERTY(config)
	float MouseSensitivity = 1.f;

	UPROPERTY(config)
	bool bInvertMouseY = false;

	/** Lumen hardware ray tracing; off = software Lumen (much faster on a MacBook). */
	UPROPERTY(config)
	bool bHardwareRayTracing = false;

	UPROPERTY(config)
	bool bNanite = true;

	UPROPERTY(config)
	bool bShowFPS = false;

	/** Dusk mode: the sun sinks below the horizon, sunlight and ambient both dim (settings menu "Dämmerung"). */
	UPROPERTY(config)
	bool bDusk = false;

	/** Old camcorder look: teal tint, grain, fringes, "CAMERA 01" overlay (settings menu "Videokamera"). */
	UPROPERTY(config)
	bool bCamcorder = false;

	/** Exposure offset in stops, -2..+2 (settings menu "Helligkeit"). */
	UPROPERTY(config)
	float Brightness = 0.f;

	/** How deep dusk mode goes, 0..1 (settings menu "Dämmerungsstärke"). */
	UPROPERTY(config)
	float DuskAmount = 1.f;

	/** Camcorder pixelation, 0..1: render resolution 100 % down to 20 %, nearest-neighbour upscale. */
	UPROPERTY(config)
	float CamPixelation = 0.3f;

	/** Fog density multiplier, 0..3 (settings menu "Nebel"). */
	UPROPERTY(config)
	float FogAmount = 1.f;

	/** Camcorder noise (film grain), 0..1 (settings menu "Rauschen (Videokamera)"). */
	UPROPERTY(config)
	float CamNoise = 0.75f;

	/** Game language: "de" or "en" (main menu / settings "Sprache"). */
	UPROPERTY(config)
	FString Language = TEXT("de");
};
