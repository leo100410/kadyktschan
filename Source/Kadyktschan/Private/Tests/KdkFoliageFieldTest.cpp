#include "Misc/AutomationTest.h"
#include "KdkFoliageField.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFoliageParseSkipsMalformedLinesTest, "Kadyktschan.Foliage.ParseSkipsMalformedLines",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FFoliageParseSkipsMalformedLinesTest::RunTest(const FString& Parameters)
{
	// Arrange: one valid line, one with a missing field, one blank line
	const FString Text = TEXT("100 -200 30 90 1.5\n1 2 3 4\n\n");
	TArray<FTransform> Out;
	// Act
	const int32 Added = AKdkFoliageField::ParseInstances(Text, Out);
	// Assert
	TestEqual(TEXT("one instance parsed"), Added, 1);
	TestEqual(TEXT("location north/east/z in cm"), Out[0].GetLocation(), FVector(100.0, -200.0, 30.0));
	TestEqual(TEXT("uniform scale"), Out[0].GetScale3D(), FVector(1.5));
	TestEqual(TEXT("yaw in degrees"), Out[0].Rotator().Yaw, 90.0, 1e-3);
	return true;
}

#endif
