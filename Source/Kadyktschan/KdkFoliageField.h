// Dense vegetation as instanced meshes: one hierarchical instanced component per layer (species variant), filled from
// a plain-text instance list written by tools/research/scatter_vegetation.py. Instances are not saved with the level;
// they are rebuilt in the editor (OnConstruction) and at game start (BeginPlay).

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "KdkFoliageField.generated.h"

class UStaticMesh;
class UHierarchicalInstancedStaticMeshComponent;

USTRUCT(BlueprintType)
struct FKdkFoliageLayer
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Foliage")
	TObjectPtr<UStaticMesh> Mesh;

	/** Instance list under Content/Kadykchan/Data/Foliage/, one "north_cm east_cm z_cm yaw_deg scale" line per instance. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Foliage")
	FString DataFile;

	/** Instances beyond this distance (cm) are culled; 0 keeps them at any distance. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Foliage")
	int32 CullEnd = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Foliage")
	bool bCastShadow = true;
};

UCLASS()
class KADYKTSCHAN_API AKdkFoliageField : public AActor
{
	GENERATED_BODY()

public:
	AKdkFoliageField();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Foliage")
	TArray<FKdkFoliageLayer> FoliageLayers;

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;

	/** Parses one instance list; malformed lines are skipped. Returns the number of transforms added. */
	static int32 ParseInstances(const FString& Text, TArray<FTransform>& Out);

private:
	void Rebuild();

	UPROPERTY(Transient)
	TArray<TObjectPtr<UHierarchicalInstancedStaticMeshComponent>> Built;
};
