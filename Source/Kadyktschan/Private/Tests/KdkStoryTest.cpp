// Story rules (Story.json loading, objective order, view picking) - Kadyktschan.Story.*

#include "Misc/AutomationTest.h"
#include "KdkStory.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
	// two objectives with two and one finds; positions in metres [north, east, z]
	const TCHAR* TwoSteps = TEXT(R"({"steps": [
		{"id": "a", "place": "A", "goal": "go to A", "done": "A done", "door": [1, 2, 0],
		 "clues": [{"id": "a1", "title": "T1", "text": "x", "pos": [0, 0, 1]}, {"id": "a2", "title": "T2", "text": "y", "pos": [0, 1, 1]}]},
		{"id": "b", "place": "B", "goal": "go to B", "done": "B done", "door": [5, 5, 0],
		 "clues": [{"id": "b1", "title": "T3", "text": "z", "pos": [10, 0, 1]}]},
		{"id": "empty", "place": "C", "goal": "", "done": "", "door": [0, 0, 0], "clues": []}]})");
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkStoryLoadTest, "Kadyktschan.Story.LoadSkipsStepsWithoutFinds",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkStoryLoadTest::RunTest(const FString& Parameters)
{
	FKdkStory Story;
	TestTrue(TEXT("loads"), Story.Load(TwoSteps));
	TestEqual(TEXT("step without finds dropped"), Story.Steps.Num(), 2);
	TestEqual(TEXT("metres become centimetres"), Story.Steps[0].Clues[1].Pos, FVector(0.0, 100.0, 100.0));
	TestFalse(TEXT("malformed json"), FKdkStory().Load(TEXT("{steps: oops")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkStoryOrderTest, "Kadyktschan.Story.StepCompletesWhenAllFindsRead",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkStoryOrderTest::RunTest(const FString& Parameters)
{
	FKdkStory Story;
	Story.Load(TwoSteps);
	TestEqual(TEXT("first find leaves the step open"), Story.Find(0, 0).Num(), 0);
	TestEqual(TEXT("still on step 0"), Story.Current, 0);
	// a later objective's find read early does not skip ahead ...
	TestEqual(TEXT("early find completes nothing"), Story.Find(1, 0).Num(), 0);
	// ... but counts once the story gets there: the last find of step 0 completes both
	const TArray<int32> Done = Story.Find(0, 1);
	TestEqual(TEXT("two steps completed"), Done.Num(), 2);
	TestTrue(TEXT("finished"), Story.IsFinished());
	TestTrue(TEXT("no current step"), Story.CurrentStep() == nullptr);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkStoryPickTest, "Kadyktschan.Story.PickTakesTheFindInView",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkStoryPickTest::RunTest(const FString& Parameters)
{
	const TArray<FVector> Points = {FVector(100, 30, 0), FVector(100, 5, 0), FVector(-100, 0, 0), FVector(500, 0, 0)};
	// looking along +X from the origin, 220 cm reach, 12 degrees: the second point (3 degrees off) wins over the
	// first (17 degrees), the one behind and the one out of reach never count
	TestEqual(TEXT("nearest to the ray"), FKdkStory::Pick(Points, FVector::ZeroVector, FVector(1, 0, 0), 220.f, 12.f), 1);
	TestEqual(TEXT("nothing in view"), FKdkStory::Pick(Points, FVector::ZeroVector, FVector(0, 0, 1), 220.f, 12.f), (int32)INDEX_NONE);
	return true;
}

#endif
