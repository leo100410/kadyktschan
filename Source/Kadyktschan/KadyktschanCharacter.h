// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Logging/LogMacros.h"
#include "KadyktschanCharacter.generated.h"

class UInputComponent;
class USkeletalMeshComponent;
class UCameraComponent;
class USpotLightComponent;
class UInputAction;
struct FInputActionValue;

DECLARE_LOG_CATEGORY_EXTERN(LogTemplateCharacter, Log, All);

/**
 *  A basic first person character
 */
UCLASS(abstract)
class AKadyktschanCharacter : public ACharacter
{
	GENERATED_BODY()

	/** Pawn mesh: first person view (arms; seen only by self) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	USkeletalMeshComponent* FirstPersonMesh;

	/** First person camera */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* FirstPersonCameraComponent;

	/** Flashlight (L): a spot on the camera, off at the start. Brightness and cone are tuned on the component. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	USpotLightComponent* Flashlight;

protected:

	/** Jump Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	UInputAction* JumpAction;

	/** Move Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	UInputAction* MoveAction;

	/** Look Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	class UInputAction* LookAction;

	/** Mouse Look Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	class UInputAction* MouseLookAction;
	
public:
	AKadyktschanCharacter();

protected:

	/** Called from Input Actions for movement input */
	void MoveInput(const FInputActionValue& Value);

	/** Called from Input Actions for looking input */
	void LookInput(const FInputActionValue& Value);

	/** Handles aim inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoAim(float Yaw, float Pitch);

	/** Handles move inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoMove(float Right, float Forward);

	/** Handles jump start inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpStart();

	/** Handles jump end inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpEnd();

protected:

	/** Set up input action bindings */
	virtual void SetupPlayerInputComponent(UInputComponent* InputComponent) override;

	virtual void Tick(float DeltaSeconds) override;

	/** Free flight for looking around the map (F): no collision, moves along the view direction. */
	void ToggleFlight();
	void SetVerticalUp() { VerticalInput = 1.f; }
	void SetVerticalDown() { VerticalInput = -1.f; }
	void SetVerticalNone() { VerticalInput = 0.f; }
	void BoostOn() { bBoost = true; ApplyFlySpeed(); ApplyWalkSpeed(); }
	void BoostOff() { bBoost = false; ApplyFlySpeed(); ApplyWalkSpeed(); }
	/** Shooter mode: slow body-camera walk, Shift sprints. Story mode keeps the template speed. */
	void ApplyWalkSpeed();
	void ToggleCrouch();
	void QReleased() { SetVerticalNone(); }
	void FlyFaster() { ChangeFlySpeed(1.25f); }
	void FlySlower() { ChangeFlySpeed(0.8f); }
	void ChangeFlySpeed(float Factor);
	void ApplyFlySpeed();

	/** Base flight speed in cm/s (mouse wheel scales it); Shift multiplies by FlyBoost. */
	UPROPERTY(EditAnywhere, Category = "Flight")
	float FlySpeed = 2500.f;

	UPROPERTY(EditAnywhere, Category = "Flight")
	float FlyBoost = 4.f;

	bool bFlying = false;
	bool bBoost = false;
	float VerticalInput = 0.f;

	// shooter mode (design/gdd/shooter-mode.md): the rifle in view and the body camera
	UPROPERTY() TObjectPtr<class UStaticMeshComponent> Rifle;
	UPROPERTY() TObjectPtr<class UPointLightComponent> MuzzleFlash;
	bool bShooter = false;
	bool bAiming = false;
	bool bReloading = false;
	float TargetFov = 90.f;
	float StoryFov = 90.f;
	float StoryWalkSpeed = 600.f;
	float Aim = 0.f;         // 0 hip .. 1 down the sights
	float ReloadPose = 0.f;
	float Kick = 0.f;        // recoil, decays
	float FlashLeft = 0.f;
	FRotator LastView = FRotator::ZeroRotator;
	FRotator Sway = FRotator::ZeroRotator;
	void UpdateRifle(float DeltaSeconds);

	// cover (Q, like RDR2): pressed against a wall or obstacle, sliding along it, popping up to aim over low cover
	bool bInCover = false;
	bool bLowCover = false;
	FVector CoverNormal = FVector::ZeroVector;  // horizontal, pointing from the cover towards the player
	FVector CoverTarget = FVector::ZeroVector;
	float CoverSnap = 0.f;                      // seconds left of the slide into cover
	float CoverTop = 0.f;                       // world height of the cover's top edge
	FVector EyeOffset = FVector::ZeroVector;    // camera offset in cover (down behind it, up or sideways to peek)
	FVector FirstPersonBase = FVector::ZeroVector;
	bool HasCoverAt(const FVector& At, float Reach, FHitResult& OutHit) const;
	void EnterCover();
	void LeaveCover();
	void UpdateCover(float DeltaSeconds);

public:

	/** Shooter mode on: rifle, wide body-camera angle Fov, sprint and crouch, no flight. Off restores the story view. */
	void SetShooterMode(bool bOn, float Fov);
	bool IsShooterMode() const { return bShooter; }
	bool IsInCover() const { return bInCover; }
	/** Q: in the shooter mode takes or leaves cover; in flight it still means "down". */
	void QPressed();
	void SetAiming(bool bOn, float Fov) { bAiming = bOn; TargetFov = Fov; }
	void SetReloading(bool bOn) { bReloading = bOn; }
	/** Muzzle flash and the rifle's kick for one shot. */
	void ShotFx();

	/** Switches the flashlight on or off (L). */
	void ToggleFlashlight();

	/** Returns the first person mesh **/
	USkeletalMeshComponent* GetFirstPersonMesh() const { return FirstPersonMesh; }

	/** Returns first person camera component **/
	UCameraComponent* GetFirstPersonCameraComponent() const { return FirstPersonCameraComponent; }

};

