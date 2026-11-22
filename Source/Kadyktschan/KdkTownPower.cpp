#include "KdkTownPower.h"
#include "KadyktschanPlayerController.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

AKdkTownPower::AKdkTownPower()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.12f;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Circuit")));
}

float AKdkTownPower::LampOutput(int32 Index, float Seconds, bool bPowered)
{
	if (!bPowered || Index % 7 == 0) return 0.f;
	// Individual, slow outages; most fixtures remain steady.
	if (Index % 5 == 0 && FMath::Fmod(Seconds + Index * 0.71f, 8.3f) < 0.65f) return 0.f;
	return 1.f;
}

void AKdkTownPower::BeginPlay()
{
	Super::BeginPlay();
	FString Json;
	TSharedPtr<FJsonObject> Data;
	const TArray<TSharedPtr<FJsonValue>>* Items;
	if (!FFileHelper::LoadFileToString(Json, *(FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/Power.json"))) ||
		!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Data) || !Data.IsValid() ||
		!Data->TryGetArrayField(TEXT("lights"), Items)) return;
	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UMaterialInterface* Glow = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Kadykchan/Materials/M_PowerBulb.M_PowerBulb"));
	for (const auto& Item : *Items)
	{
		const TSharedPtr<FJsonObject> Obj = Item->AsObject();
		const TArray<TSharedPtr<FJsonValue>>* P;
		bool bIndoor = false;
		if (!Obj.IsValid() || !Obj->TryGetArrayField(TEXT("pos"), P) || P->Num() != 3 ||
			!Obj->TryGetBoolField(TEXT("indoor"), bIndoor)) continue;
		FVector Pos((*P)[0]->AsNumber()*100, (*P)[1]->AsNumber()*100, (*P)[2]->AsNumber()*100);
		if (Pos.ContainsNaN()) continue;
		UPointLightComponent* Light;
		if (bIndoor) Light = NewObject<UPointLightComponent>(this);
		else
		{
			USpotLightComponent* Spot = NewObject<USpotLightComponent>(this);
			Spot->SetInnerConeAngle(45.f);
			Spot->SetOuterConeAngle(65.f);
			Light = Spot;
		}
		AddInstanceComponent(Light);
		Light->SetupAttachment(GetRootComponent());
		Light->SetMobility(EComponentMobility::Movable);
		Light->SetIntensityUnits(ELightUnits::Lumens);
		Light->SetIntensity(bIndoor ? 170.f : 1300.f);
		Light->SetLightColor(FLinearColor(1.f, 0.60f, 0.23f));
		Light->SetAttenuationRadius(bIndoor ? 650.f : 1700.f);
		Light->SetCastShadows(bIndoor);
		Light->SetVisibility(false);
		Light->RegisterComponent();
		Light->SetWorldLocation(Pos);
		Light->SetWorldRotation(FRotator(-90,0,0));
		Lights.Add(Light);
		UStaticMeshComponent* Bulb = NewObject<UStaticMeshComponent>(this);
		AddInstanceComponent(Bulb);
		Bulb->SetupAttachment(GetRootComponent());
		Bulb->SetStaticMesh(Sphere);
		if (Glow) Bulb->SetMaterial(0,Glow);
		Bulb->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Bulb->SetCastShadow(false);
		Bulb->SetVisibility(false);
		Bulb->RegisterComponent();
		Bulb->SetWorldLocation(Pos);
		Bulb->SetWorldScale3D(bIndoor ? FVector(0.08) : FVector(0.28,0.12,0.06));
		Bulbs.Add(Bulb);
	}
}

void AKdkTownPower::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const AKadyktschanPlayerController* PC = Cast<AKadyktschanPlayerController>(GetWorld()->GetFirstPlayerController());
	const bool bPowered = PC && PC->IsTownPowerOn();
	for (int32 I=0; I<Lights.Num(); ++I)
	{
		const bool bOn = LampOutput(I, GetWorld()->GetTimeSeconds(), bPowered) > 0.f;
		Bulbs[I]->SetVisibility(bOn);
		Lights[I]->SetVisibility(bOn);
	}
}
