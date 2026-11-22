#include "KdkStory.h"

#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
	FVector ReadMetres(const TSharedPtr<FJsonObject>& O, const TCHAR* Field)
	{
		const TArray<TSharedPtr<FJsonValue>>* A;
		if (!O->TryGetArrayField(Field, A) || A->Num() < 3)
		{
			return FVector::ZeroVector;
		}
		return FVector((*A)[0]->AsNumber(), (*A)[1]->AsNumber(), (*A)[2]->AsNumber()) * 100.0;  // [north, east, z] m -> cm
	}
}

bool FKdkStory::Load(const FString& Json)
{
	Steps.Reset();
	Current = 0;
	TSharedPtr<FJsonObject> Root;
	const TArray<TSharedPtr<FJsonValue>>* Items;
	if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Root) || !Root.IsValid() || !Root->TryGetArrayField(TEXT("steps"), Items))
	{
		return false;
	}
	for (const TSharedPtr<FJsonValue>& V : *Items)
	{
		const TSharedPtr<FJsonObject> O = V->AsObject();
		const TArray<TSharedPtr<FJsonValue>>* ClueItems;
		if (!O.IsValid() || !O->TryGetArrayField(TEXT("clues"), ClueItems) || ClueItems->Num() == 0)
		{
			continue;
		}
		FKdkStoryStep Step;
		Step.Id = O->GetStringField(TEXT("id"));
		O->TryGetBoolField(TEXT("sequential"), Step.bSequential);
		Step.Place = O->GetStringField(TEXT("place"));
		Step.Goal = O->GetStringField(TEXT("goal"));
		Step.Done = O->GetStringField(TEXT("done"));
		Step.Door = ReadMetres(O, TEXT("door"));
		O->TryGetStringField(TEXT("place_en"), Step.PlaceEn);
		O->TryGetStringField(TEXT("goal_en"), Step.GoalEn);
		O->TryGetStringField(TEXT("done_en"), Step.DoneEn);
		for (const TSharedPtr<FJsonValue>& C : *ClueItems)
		{
			const TSharedPtr<FJsonObject> CO = C->AsObject();
			if (!CO.IsValid())
			{
				continue;
			}
			FKdkClue& Clue = Step.Clues.AddDefaulted_GetRef();
			Clue.Id = CO->GetStringField(TEXT("id"));
			Clue.Title = CO->GetStringField(TEXT("title"));
			Clue.Text = CO->GetStringField(TEXT("text"));
			Clue.Pos = ReadMetres(CO, TEXT("pos"));
			CO->TryGetStringField(TEXT("title_en"), Clue.TitleEn);
			CO->TryGetStringField(TEXT("text_en"), Clue.TextEn);
		}
		Steps.Add(MoveTemp(Step));
	}
	return Steps.Num() > 0;
}

bool FKdkStory::IsStepComplete(int32 Step) const
{
	if (!Steps.IsValidIndex(Step))
	{
		return false;
	}
	for (const FKdkClue& C : Steps[Step].Clues)
	{
		if (!C.bFound)
		{
			return false;
		}
	}
	return true;
}

bool FKdkStory::CanFind(int32 Step, int32 Clue) const
{
	if (!Steps.IsValidIndex(Step) || !Steps[Step].Clues.IsValidIndex(Clue)) return false;
	if (!Steps[Step].bSequential) return true;
	if (Step > Current) return false;
	for (int32 I = 0; I < Clue; ++I)
	{
		if (!Steps[Step].Clues[I].bFound) return false;
	}
	return true;
}

TArray<int32> FKdkStory::Find(int32 Step, int32 Clue)
{
	TArray<int32> Completed;
	if (!CanFind(Step, Clue))
	{
		return Completed;
	}
	Steps[Step].Clues[Clue].bFound = true;
	while (!IsFinished() && IsStepComplete(Current))
	{
		Completed.Add(Current++);
	}
	return Completed;
}

void FKdkStory::SkipTo(int32 Step)
{
	Current = FMath::Clamp(Step, 0, Steps.Num());
	for (int32 S = 0; S < Current; ++S)
	{
		for (FKdkClue& C : Steps[S].Clues)
		{
			C.bFound = true;
		}
	}
}

int32 FKdkStory::Pick(const TArray<FVector>& Points, const FVector& Eye, const FVector& Dir, float MaxDist, float MaxAngleDeg)
{
	const float MinCos = FMath::Cos(FMath::DegreesToRadians(MaxAngleDeg));
	int32 Best = INDEX_NONE;
	float BestCos = MinCos;
	for (int32 I = 0; I < Points.Num(); ++I)
	{
		const FVector To = Points[I] - Eye;
		const float Dist = To.Size();
		if (Dist > MaxDist || Dist < KINDA_SMALL_NUMBER)
		{
			continue;
		}
		const float Cos = FVector::DotProduct(To / Dist, Dir.GetSafeNormal());
		if (Cos >= BestCos)
		{
			BestCos = Cos;
			Best = I;
		}
	}
	return Best;
}
