#include "Misc/AutomationTest.h"
#include "KdkSkyCycle.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
	// fixture: distinct values so each assertion can only pass for the right field
	FKdkSkyCycleParams MakeParams()
	{
		FKdkSkyCycleParams P;
		P.StartAzimuth = 180.f;
		P.EndAzimuth = 360.f;
		P.StartElevation = 40.f;
		P.EndElevation = 4.f;
		P.StartTemperatureK = 5800.f;
		P.EndTemperatureK = 4500.f;
		return P;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkyCycleStartTest, "Kadyktschan.SkyCycle.StartReturnsStartState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FSkyCycleStartTest::RunTest(const FString& Parameters)
{
	// Arrange
	const FKdkSkyCycleParams P = MakeParams();
	// Act
	const FKdkSkyState S = EvaluateSkyCycle(P, 0.f);
	// Assert
	TestEqual(TEXT("azimuth at start"), S.Azimuth, 180.f);
	TestEqual(TEXT("elevation at start"), S.Elevation, 40.f);
	TestEqual(TEXT("temperature at start"), S.TemperatureK, 5800.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkyCycleEndTest, "Kadyktschan.SkyCycle.EndReturnsWhiteNightState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FSkyCycleEndTest::RunTest(const FString& Parameters)
{
	const FKdkSkyCycleParams P = MakeParams();
	const FKdkSkyState S = EvaluateSkyCycle(P, 1.f);
	TestEqual(TEXT("azimuth at end"), S.Azimuth, 360.f);
	TestEqual(TEXT("elevation at end"), S.Elevation, 4.f);
	TestEqual(TEXT("temperature at end"), S.TemperatureK, 4500.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkyCycleClampTest, "Kadyktschan.SkyCycle.OutsideRangeIsClamped",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FSkyCycleClampTest::RunTest(const FString& Parameters)
{
	const FKdkSkyCycleParams P = MakeParams();
	TestEqual(TEXT("before start = start"), EvaluateSkyCycle(P, -0.5f).Elevation, 40.f);
	TestEqual(TEXT("after end = end"), EvaluateSkyCycle(P, 1.7f).Elevation, 4.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkyCycleMonotonicTest, "Kadyktschan.SkyCycle.SunSinksMonotonically",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FSkyCycleMonotonicTest::RunTest(const FString& Parameters)
{
	const FKdkSkyCycleParams P = MakeParams();
	float Previous = EvaluateSkyCycle(P, 0.f).Elevation;
	for (int32 Step = 1; Step <= 20; ++Step)
	{
		const float Current = EvaluateSkyCycle(P, Step / 20.f).Elevation;
		TestTrue(FString::Printf(TEXT("elevation does not rise at step %d"), Step), Current <= Previous);
		Previous = Current;
	}
	// smoothstep: half time is exactly half way, the ends are eased
	TestEqual(TEXT("midpoint elevation"), EvaluateSkyCycle(P, 0.5f).Elevation, 22.f);
	return true;
}

#endif
