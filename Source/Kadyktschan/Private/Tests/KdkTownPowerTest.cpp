#include "Misc/AutomationTest.h"
#include "KdkTownPower.h"
#include "KdkStory.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkTownPowerTest, "Kadyktschan.Power.RepairAndLampStates",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkTownPowerTest::RunTest(const FString& Parameters)
{
	FKdkStory Story;
	TestTrue(TEXT("repair loads"),Story.Load(TEXT(R"({"steps":[{"id":"power","place":"P","goal":"G","done":"D","sequential":true,"door":[0,0,0],"clues":[{"id":"inspect","title":"A","text":"A","pos":[0,0,1]},{"id":"fuse","title":"B","text":"B","pos":[1,0,1]},{"id":"start","title":"C","text":"C","pos":[2,0,1]}]}]})")));
	Story.Find(0,2);
	TestFalse(TEXT("cannot start before repair"),Story.Steps[0].Clues[2].bFound);
	Story.Find(0,0); Story.Find(0,1);
	TestFalse(TEXT("fuse alone leaves power off"),Story.IsStepComplete(0));
	Story.Find(0,2);
	TestTrue(TEXT("start completes repair"),Story.IsStepComplete(0));
	TestEqual(TEXT("power off"),AKdkTownPower::LampOutput(1,1,false),0.f);
	TestEqual(TEXT("broken stays dark"),AKdkTownPower::LampOutput(7,3,true),0.f);
	TestEqual(TEXT("working stays on"),AKdkTownPower::LampOutput(1,3,true),1.f);
	TestEqual(TEXT("bad contact off phase"),AKdkTownPower::LampOutput(5,4.9f,true),0.f);
	TestEqual(TEXT("bad contact on phase"),AKdkTownPower::LampOutput(5,1,true),1.f);
	return true;
}
#endif
