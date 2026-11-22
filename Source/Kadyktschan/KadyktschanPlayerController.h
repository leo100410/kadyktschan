// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "KdkStory.h"
#include "SKdkStoryHud.h"
#include "Scalability.h"
#include "KadyktschanPlayerController.generated.h"

class UInputMappingContext;
class UUserWidget;

/**
 *  Simple first person Player Controller
 *  Manages the input mapping context.
 *  Overrides the Player Camera Manager class.
 */
UCLASS(abstract, config="Game")
class KADYKTSCHAN_API AKadyktschanPlayerController : public APlayerController
{
	GENERATED_BODY()
	
public:

	/** Constructor */
	AKadyktschanPlayerController();

protected:

	/** Input Mapping Contexts */
	UPROPERTY(EditAnywhere, Category="Input|Input Mappings")
	TArray<UInputMappingContext*> DefaultMappingContexts;

	/** Input Mapping Contexts */
	UPROPERTY(EditAnywhere, Category="Input|Input Mappings")
	TArray<UInputMappingContext*> MobileExcludedMappingContexts;

	/** Mobile controls widget to spawn */
	UPROPERTY(EditAnywhere, Category="Input|Touch Controls")
	TSubclassOf<UUserWidget> MobileControlsWidgetClass;

	/** Pointer to the mobile controls widget */
	UPROPERTY()
	TObjectPtr<UUserWidget> MobileControlsWidget;

	/** If true, the player will use UMG touch controls even if not playing on mobile platforms */
	UPROPERTY(EditAnywhere, Config, Category = "Input|Touch Controls")
	bool bForceTouchControls = false;

	/** Gameplay initialization */
	virtual void BeginPlay() override;

	/** Input mapping context setup */
	virtual void SetupInputComponent() override;

	/** Returns true if the player should use UMG touch controls */
	bool ShouldUseTouchControls() const;

	/** Opens or closes the settings menu (Esc, or M - Esc ends play in the editor). Pauses the game while open. */
	void ToggleSettingsMenu();

public:
	/** Shows or hides the town map (K or Tab). The game keeps running; the map follows the player. */
	void ToggleTownMap();
	void ToggleFurnishingMap();

	/** E: reads the find in view (marks it, may complete the objective), or closes the open text. */
	void StoryInteract();

	/** N: opens or closes the notebook (objectives so far and what was found). */
	void ToggleNotebook();

	/** Shows the main menu (title picture, start, settings, language, quit) and pauses the game behind it. */
	void ShowMainMenu();

	/** Dev start: opens objective Step with everything before it read. */
	void StorySkipTo(int32 Step) { Story.SkipTo(Step); }
	/** Story: after the power station repair. Shooter mode: the round's backup power switch. */
	bool IsTownPowerOn() const;

	/** Shooter mode "Einsatz" (main menu): a round in the same world, the story state is kept. Seed < 0: random. */
	void StartShooter(int32 Seed = -1);
	/** Back from a round: everything it spawned is removed, then the main menu. */
	void EndShooter();
	bool IsShooter() const { return Shooter.IsValid(); }
	/** A hit: the camcorder breaks down at once, not at the next half-second check. */
	void OnShooterHurt();
	void ShowShooterResult(const FString& Title, const FString& Text);
	class AKdkShooterDirector* GetShooter() const { return Shooter.Get(); }

protected:
	/** Story focus, marker and objective, refreshed every frame for the overlay. */
	virtual void PlayerTick(float DeltaTime) override;

	/** Re-levels the view once the window has settled (see BeginPlay). */
	void LevelStartView();

	/** Shows or hides the camcorder look to match the settings (checked twice a second). */
	void UpdateCamcorder();

private:
	TWeakObjectPtr<class APostProcessVolume> CamVolume;
	TSharedPtr<class SWidget> CamOverlay;
	FTimerHandle CamTimer;
	TSharedPtr<class SWidget> SettingsMenu;
	TSharedPtr<class SWidget> SettingsMenuViewportEntry;
	TSharedPtr<class SWidget> TownMap;
	TSharedPtr<class SWidget> FurnishingMap;
	FTimerHandle StartViewTimer;
	FKdkStory Story;
	FKdkHudState Hud;
	TSharedPtr<class SWidget> StoryHud;
	int32 FocusStep = INDEX_NONE;
	int32 FocusClue = INDEX_NONE;
	TArray<TPair<FString, FString>> PendingTexts;  // "objective done" panels shown after the find that closed it
	TSharedPtr<class SWidget> MainMenu;
	UPROPERTY()
	TObjectPtr<class UTexture2D> TitleTexture;  // kept alive for the menu's brush
	FSlateBrush TitleBrush;
	bool bFpsHiddenForMenu = false;  // "stat fps" is a toggle: hidden while the title picture shows
	void CloseMainMenu();

	TWeakObjectPtr<class AKdkShooterDirector> Shooter;
	void FireOn();
	void FireOff();
	void AimOn();
	void AimOff();
	void ReloadKey();

	// shooter mode: dynamic graphics (frame rate below Shooter.json target_fps -> lower levels, restored afterwards)
	void UpdatePerformance(float DeltaTime);
	void SetPerfLevel(int32 Level);
	int32 PerfLevel = 0;
	float DynScale = 1.f;      // resolution factor of the level
	float PerfTime = 0.f;
	int32 PerfFrames = 0;
	float BelowFor = 0.f;
	float AboveFor = 0.f;
	Scalability::FQualityLevels SavedQuality;
};
