#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KdkTownPower.generated.h"

// Fictional backup lighting circuit, controlled by the existing repair objective.
UCLASS()
class KADYKTSCHAN_API AKdkTownPower : public AActor
{
	GENERATED_BODY()
public:
	AKdkTownPower();
	static float LampOutput(int32 Index, float Seconds, bool bPowered);
protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
private:
	UPROPERTY() TArray<TObjectPtr<class UPointLightComponent>> Lights;
	UPROPERTY() TArray<TObjectPtr<class UStaticMeshComponent>> Bulbs;
};
