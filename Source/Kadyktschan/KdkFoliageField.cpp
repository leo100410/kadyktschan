#include "KdkFoliageField.h"

#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

AKdkFoliageField::AKdkFoliageField()
{
	PrimaryActorTick.bCanEverTick = false;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	RootComponent->SetMobility(EComponentMobility::Static);
}

int32 AKdkFoliageField::ParseInstances(const FString& Text, TArray<FTransform>& Out)
{
	TArray<FString> Lines;
	Text.ParseIntoArrayLines(Lines);
	const int32 Before = Out.Num();
	Out.Reserve(Before + Lines.Num());
	TArray<FString> V;
	for (const FString& L : Lines)
	{
		V.Reset();
		L.ParseIntoArrayWS(V);
		if (V.Num() != 5)
		{
			continue;
		}
		const float Scale = FCString::Atof(*V[4]);
		Out.Emplace(FRotator(0.f, FCString::Atof(*V[3]), 0.f),
			FVector(FCString::Atof(*V[0]), FCString::Atof(*V[1]), FCString::Atof(*V[2])), FVector(Scale));
	}
	return Out.Num() - Before;
}

void AKdkFoliageField::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (GetWorld() && !GetWorld()->IsGameWorld())
	{
		Rebuild();
	}
}

void AKdkFoliageField::BeginPlay()
{
	Super::BeginPlay();
	Rebuild();
}

void AKdkFoliageField::Rebuild()
{
	for (UHierarchicalInstancedStaticMeshComponent* C : Built)
	{
		if (C)
		{
			C->DestroyComponent();
		}
	}
	Built.Reset();
	const FString Dir = FPaths::ProjectContentDir() / TEXT("Kadykchan/Data/Foliage");
	for (const FKdkFoliageLayer& Layer : FoliageLayers)
	{
		FString Text;
		TArray<FTransform> Instances;
		if (!Layer.Mesh || !FFileHelper::LoadFileToString(Text, *(Dir / Layer.DataFile)) || ParseInstances(Text, Instances) == 0)
		{
			UE_LOG(LogTemp, Warning, TEXT("Foliage: layer %s skipped (mesh or %s missing)"), *GetNameSafe(Layer.Mesh), *Layer.DataFile);
			continue;
		}
		UHierarchicalInstancedStaticMeshComponent* C = NewObject<UHierarchicalInstancedStaticMeshComponent>(this, NAME_None, RF_Transient);
		C->SetMobility(EComponentMobility::Static);
		C->SetStaticMesh(Layer.Mesh);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);  // thickets must not wall off the town
		C->SetCastShadow(Layer.bCastShadow);
		C->SetCullDistances(0, Layer.CullEnd);
		C->SetupAttachment(RootComponent);
		C->RegisterComponent();
		C->AddInstances(Instances, false, true);
		Built.Add(C);
	}
}
