#include "Misc/AutomationTest.h"
#include "SKdkTownMap.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkMapMarkersTest,"Kadyktschan.Map.ClusteredMarkersStayLinkedAndSeparate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkMapMarkersTest::RunTest(const FString& Parameters)
{
	TArray<FVector2f> Anchors;
	for (int32 I=0; I<11; ++I) Anchors.Add(FVector2f(200+I,200));
	const FBox2f Area(FVector2f(20,20),FVector2f(600,450));
	const auto Markers=SKdkTownMap::LayoutMarkers(Anchors,Area);
	TestEqual(TEXT("one badge for each place"),Markers.Num(),Anchors.Num());
	for (int32 I=0; I<Markers.Num(); ++I)
	{
		TestTrue(TEXT("inside chart"),Area.IsInsideOrOn(Markers[I]));
		for (int32 J=0; J<I; ++J) TestTrue(TEXT("badges do not overlap"),(Markers[I]-Markers[J]).SizeSquared()>=26.f*26.f);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkMapDetailsTest,"Kadyktschan.Map.LoadFurnishedFloorsAndReset",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkMapDetailsTest::RunTest(const FString& Parameters)
{
	FKdkTownPlan Plan;
	const FString Json=TEXT(R"({"buildings":[[10,20,30,12,0]],"places":[{"name":"Haus","kind":"base","east_m":10,"north_m":20,"entry":[12,18],"floors":3,"details":"EG: A / B"}]})");
	TestTrue(TEXT("loads"),SKdkTownMap::LoadPlan(Json,Plan));
	TestEqual(TEXT("three furnished floors"),Plan.Places[0].Floors,3);
	TestTrue(TEXT("entry is separate from building centre"),Plan.Places[0].Entry.Equals(FVector2f(12,18)));
	TestFalse(TEXT("malformed rejected"),SKdkTownMap::LoadPlan(TEXT("oops"),Plan));
	TestEqual(TEXT("old places removed on reload"),Plan.Places.Num(),0);
	return true;
}
#endif
