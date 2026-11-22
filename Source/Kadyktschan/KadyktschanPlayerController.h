// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
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
	FTimerHandle StartViewTimer;
};
