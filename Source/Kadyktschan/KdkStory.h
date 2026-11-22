// Story path: objectives in order, each with finds the player inspects (E). Plain data + rules, no UObject, so the
// automation tests can drive it; loaded from Content/Kadykchan/Data/Story.json (tools/research/story_data.py).

#pragma once

#include "CoreMinimal.h"

struct FKdkClue
{
	FString Id;
	FString Title;
	FString Text;
	FString TitleEn;  // English (empty: the German text is shown)
	FString TextEn;
	FVector Pos = FVector::ZeroVector;  // world centimetres (X north, Y east)
	bool bFound = false;
};

struct FKdkStoryStep
{
	FString Id;
	FString Place;
	FString Goal;
	FString Done;
	FString PlaceEn;
	FString GoalEn;
	FString DoneEn;
	bool bSequential = false;  // repairs must be performed in order
	FVector Door = FVector::ZeroVector;  // where the marker points while the player is still outside
	TArray<FKdkClue> Clues;
};

struct KADYKTSCHAN_API FKdkStory
{
	TArray<FKdkStoryStep> Steps;
	int32 Current = 0;  // index of the open objective; Steps.Num() once the story is through

	/** Parses Story.json; false (and no steps) when it is malformed or empty. Steps without finds are skipped. */
	bool Load(const FString& Json);

	/** Marks a find as read. Finds of later objectives count too: when the story reaches them they are already done.
	 *  Returns the objectives completed by this find, in order (usually none or one). */
	TArray<int32> Find(int32 Step, int32 Clue);

	bool IsStepComplete(int32 Step) const;
	bool CanFind(int32 Step, int32 Clue) const;
	bool IsFinished() const { return Current >= Steps.Num(); }
	const FKdkStoryStep* CurrentStep() const { return Steps.IsValidIndex(Current) ? &Steps[Current] : nullptr; }

	/** Opens objective Step directly, all finds before it read (dev start and tests). */
	void SkipTo(int32 Step);

	/** The point the view rests on: nearest to the view ray within MaxDist (cm) and MaxAngleDeg of it; INDEX_NONE if
	 *  none. Points behind the eye never count. */
	static int32 Pick(const TArray<FVector>& Points, const FVector& Eye, const FVector& Dir, float MaxDist, float MaxAngleDeg);
};
