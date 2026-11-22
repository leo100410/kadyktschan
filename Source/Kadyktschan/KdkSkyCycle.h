// Slow day -> white-night sky cycle (art bible 2: states A1 "Tag" and A2 "Weißnacht"; user decision 2026-11-07:
// time runs slowly over a session). Values live in a data asset; the evaluation is a pure function so it is testable.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameFramework/Actor.h"
#include "KdkSkyCycle.generated.h"

class ADirectionalLight;

/** Sun position and colour at both ends of the cycle. Azimuth in degrees clockwise from north (UE +X), elevation above the horizon. */
USTRUCT(BlueprintType)
struct FKdkSkyCycleParams
{
	GENERATED_BODY()

	/** Real-time minutes from the start state to the end state. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1.0"))
	float DurationMinutes = 90.f;

	/** A1 day: high southern sun (art bible 2: 35-50 deg at 63 N). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	float StartAzimuth = 180.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "-10.0", ClampMax = "90.0"))
	float StartElevation = 40.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1000.0", ClampMax = "12000.0"))
	float StartTemperatureK = 5800.f;

	/** A2 white night: the sun skims the northern horizon (art bible 2: 2-6 deg). 6500 K (neutral) is above the art
	 *  bible's 4300-4800 K on purpose: Sky Atmosphere already turns a 6 deg sun golden, and 4500 K read as saturated
	 *  orange (tuned 2026-11-07; DA_SkyCycle holds the live values). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	float EndAzimuth = 355.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "-10.0", ClampMax = "90.0"))
	float EndElevation = 6.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1000.0", ClampMax = "12000.0"))
	float EndTemperatureK = 6500.f;
};

/** Sun state at one moment. */
struct FKdkSkyState
{
	float Azimuth = 0.f;
	float Elevation = 0.f;
	float TemperatureK = 0.f;
	float SunIntensityScale = 1.f;
	float SkyIntensityScale = 1.f;
};

/** Pure evaluation: eased cycle T and clamped dusk amount; full dusk dims sunlight and ambient together. */
KADYKTSCHAN_API FKdkSkyState EvaluateSkyCycle(const FKdkSkyCycleParams& Params, float T, float DuskAmount = 0.f);

/** Designer-facing data asset holding the cycle parameters (coding standard: gameplay values are data-driven). */
UCLASS(BlueprintType)
class KADYKTSCHAN_API UKdkSkyCycleSettings : public UDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ShowOnlyInnerProperties))
	FKdkSkyCycleParams Params;
};

/**
 * Drives the sun directional light through the cycle at runtime. The light must be Movable.
 * -KdkSkyTime=<0..1> on the command line starts at that point of the cycle (preview and evidence shots).
 */
UCLASS()
class KADYKTSCHAN_API AKdkSkyCycleActor : public AActor
{
	GENERATED_BODY()

public:
	AKdkSkyCycleActor();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Applies the state for normalised time T to the sun. */
	void ApplyAt(float T);

	UPROPERTY(EditAnywhere, Category = "Sky")
	TObjectPtr<UKdkSkyCycleSettings> Settings;

	UPROPERTY(EditInstanceOnly, Category = "Sky")
	TObjectPtr<ADirectionalLight> Sun;

private:
	float ElapsedSeconds = 0.f;
	float TimeScale = 1.f;
	/** Sun intensity from the level, captured on first apply (dusk mode scales it). */
	float BaseIntensity = -1.f;
	float BaseFog = -1.f;
	float BaseSkyIntensity = -1.f;
	FLinearColor BaseFogLuminance = FLinearColor(-1.f, 0.f, 0.f);
};
