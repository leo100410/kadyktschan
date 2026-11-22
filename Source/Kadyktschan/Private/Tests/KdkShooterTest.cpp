// Shooter mode rules (Shooter.json loading, round setup, damage, camcorder breakdown, pickups, ammunition) -
// Kadyktschan.Shooter.*

#include "Misc/AutomationTest.h"
#include "KdkShooter.h"

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
	// three tasks, two flats, three road exits on a line; positions in metres [north, east, z]
	const TCHAR* Data = TEXT(R"({
		"tuning": {"player": {"health": 100, "mag": 30, "reserve": 40},
		           "enemies": {"looter": {"health": 80, "range_m": 50}},
		           "distortion_exponent": 1.0, "tasks_per_round": 2, "pickup_share": 1.0},
		"items": {"bandage": {"heal": 35}, "vest": {"armor": 50}, "ammo": {"rounds": 60}},
		"flats": [{"where": "A, EG links", "item": "bandage", "points": [[1, 1, 1], [2, 2, 1]]},
		          {"where": "B, 1. OG rechts", "item": "vest", "points": [[5, 5, 4]]}],
		"tasks": [{"id": "radio", "kind": "fetch_flat", "goal": "Funkgerät in {where}", "done": "ok"},
		          {"id": "power", "kind": "power_on", "pos": [0, 10, 0], "goal": "Strom", "done": "ok"},
		          {"id": "jam", "kind": "jam", "pos": [0, 20, 0], "goal": "Störsender", "done": "ok"}],
		"starts": [[0, 0, 0, 90], [0, 100, 0, -90], [0, 40, 0, 0]],
		"area": {"north": [-10, 10], "east": [0, 100], "z": [-20, 60]}})");

	FKdkShooter Loaded()
	{
		FKdkShooter S;
		S.Load(Data);
		return S;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterLoadTest, "Kadyktschan.Shooter.LoadReadsTuningAndConvertsMetres",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterLoadTest::RunTest(const FString& Parameters)
{
	FKdkShooter S;
	TestTrue(TEXT("loads"), S.Load(Data));
	TestEqual(TEXT("enemy range metres -> cm"), S.Enemies.FindChecked(TEXT("looter")).Range, 5000.f);
	TestEqual(TEXT("start yaw"), S.Starts[1].Yaw, -90.f);
	TestEqual(TEXT("start position cm"), S.Starts[1].Pos, FVector(0.0, 10000.0, 0.0));
	TestEqual(TEXT("area east cm"), S.Area.Max.Y, 10000.0);
	TestFalse(TEXT("malformed json"), FKdkShooter().Load(TEXT("{tasks: oops")));
	TestFalse(TEXT("no starts"), FKdkShooter().Load(TEXT(R"({"tasks": [], "flats": []})")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterRoundTest, "Kadyktschan.Shooter.BeginRoundIsSeededAndPicksFarthestExit",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterRoundTest::RunTest(const FString& Parameters)
{
	FKdkShooter A = Loaded(), B = Loaded();
	A.BeginRound(7);
	B.BeginRound(7);
	TestEqual(TEXT("tasks per round"), A.Tasks.Num(), 2);
	TestNotEqual(TEXT("two different tasks"), A.Tasks[0].Id, A.Tasks[1].Id);
	TestTrue(TEXT("same seed, same tasks"), A.Tasks[0].Id == B.Tasks[0].Id && A.Tasks[1].Id == B.Tasks[1].Id);
	TestEqual(TEXT("same seed, same start"), A.Start, B.Start);
	TestEqual(TEXT("pickup share 1: every flat stocked"), A.Pickups.Num(), 2);
	TestEqual(TEXT("full magazine"), A.Mag, 30);
	// the pick-up point is the exit farthest from the start: the ends of the line swap, the middle goes to an end
	const float Far = FVector::Dist2D(A.Starts[A.Start].Pos, A.Starts[A.Extract].Pos);
	for (const FKdkPlaced& P : A.Starts)
	{
		TestTrue(TEXT("no exit farther than the pick-up"), FVector::Dist2D(A.Starts[A.Start].Pos, P.Pos) <= Far);
	}
	// the radio flat's text is filled in and its pickup does not share the radio's spot
	for (int32 Seed = 0; Seed < 20; ++Seed)
	{
		FKdkShooter S = Loaded();
		S.BeginRound(Seed);
		for (const FKdkTask& T : S.Tasks)
		{
			if (T.Kind != TEXT("fetch_flat")) continue;
			TestFalse(TEXT("placeholder replaced"), T.Goal.Contains(TEXT("{where}")));
			for (const FKdkPickup& P : S.Pickups)
			{
				TestFalse(TEXT("pickup not on the radio"), P.Pos.Equals(T.Pos));
			}
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterHitTest, "Kadyktschan.Shooter.VestTakesSixtyPercentWhileItLasts",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterHitTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(1);
	TestEqual(TEXT("unprotected hit"), S.Hit(20.f), 80.f);
	S.Armor = 10.f;
	// 60 % of 20 = 12, but only 10 armour left: 10 absorbed, 10 through
	TestEqual(TEXT("vest runs out"), S.Hit(20.f), 70.f);
	TestEqual(TEXT("vest gone"), S.Armor, 0.f);
	S.Hit(500.f);
	TestTrue(TEXT("down"), S.IsDown());
	TestEqual(TEXT("health never negative"), S.Health, 0.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterDistortionTest, "Kadyktschan.Shooter.CamcorderBreaksDownWithLostHealth",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterDistortionTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(1);
	TestEqual(TEXT("intact at full health"), S.Distortion(), 0.f);
	S.Hit(50.f);
	TestEqual(TEXT("exponent 1: half health, half broken"), S.Distortion(), 0.5f);
	S.DistortionExponent = 0.8f;
	TestTrue(TEXT("exponent below 1 shows early hits more"), S.Distortion() > 0.5f);
	S.Hit(500.f);
	TestEqual(TEXT("fully broken when down"), S.Distortion(), 1.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterPickupTest, "Kadyktschan.Shooter.PickupsHealCappedAndAreNotWasted",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterPickupTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(3);
	const int32 Bandage = S.Pickups.IndexOfByPredicate([](const FKdkPickup& P) { return P.Item == TEXT("bandage"); });
	const int32 Vest = S.Pickups.IndexOfByPredicate([](const FKdkPickup& P) { return P.Item == TEXT("vest"); });
	TestFalse(TEXT("bandage refused at full health"), S.Take(Bandage));
	TestFalse(TEXT("... and stays there"), S.Pickups[Bandage].bTaken);
	S.Health = 90.f;
	TestTrue(TEXT("bandage used"), S.Take(Bandage));
	TestEqual(TEXT("heal capped at max"), S.Health, 100.f);
	TestFalse(TEXT("gone after use"), S.Take(Bandage));
	TestTrue(TEXT("vest at full health"), S.Take(Vest));
	TestEqual(TEXT("armour"), S.Armor, 50.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterAmmoTest, "Kadyktschan.Shooter.ReloadMovesOnlyWhatIsLeft",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterAmmoTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(1);
	TestFalse(TEXT("full magazine: no reload"), S.CanReload());
	for (int32 I = 0; I < 30; ++I) S.Shoot();
	TestFalse(TEXT("empty magazine"), S.Shoot());
	S.Reload();
	TestEqual(TEXT("refilled"), S.Mag, 30);
	TestEqual(TEXT("reserve 40 - 30"), S.Reserve, 10);
	for (int32 I = 0; I < 30; ++I) S.Shoot();
	S.Reload();
	TestEqual(TEXT("only 10 left"), S.Mag, 10);
	TestFalse(TEXT("reserve empty"), S.CanReload());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterTaskTest, "Kadyktschan.Shooter.TasksCompleteInOrder",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterTaskTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(5);
	TestFalse(TEXT("first of two"), S.CompleteTask());
	TestTrue(TEXT("first marked done"), S.Tasks[0].bDone);
	TestTrue(TEXT("second closes the list"), S.CompleteTask());
	TestTrue(TEXT("all done"), S.AllTasksDone());
	TestTrue(TEXT("no open task"), S.CurrentTask() == nullptr);
	TestFalse(TEXT("nothing more to complete"), S.CompleteTask());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKdkShooterRecoverTest, "Kadyktschan.Shooter.SightRecoversFasterAndDropsToHealthOnHit",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FKdkShooterRecoverTest::RunTest(const FString& Parameters)
{
	FKdkShooter S = Loaded();
	S.BeginRound(1);
	S.RegenDelay = 5.f;
	S.HealthRegen = 1.f;
	S.VisionRegen = 10.f;
	S.Hit(60.f);
	TestEqual(TEXT("sight follows the hit"), S.Vision, 40.f);
	S.Recover(4.f);
	TestEqual(TEXT("nothing before the delay"), S.Health, 40.f);
	S.Recover(1.f);  // the delay is reached within this second: it already counts
	S.Recover(2.f);
	TestEqual(TEXT("health: 3 s x 1"), S.Health, 43.f);
	TestEqual(TEXT("sight: 3 s x 10"), S.Vision, 70.f);
	S.Hit(10.f);
	TestEqual(TEXT("a new hit drops the sight straight to the health left"), S.Vision, 33.f);
	S.Recover(5.f);
	S.Recover(100.f);
	TestEqual(TEXT("health capped"), S.Health, 100.f);
	TestEqual(TEXT("sight capped"), S.Vision, 100.f);
	S.Hit(500.f);
	S.Recover(100.f);
	TestEqual(TEXT("no recovery once down"), S.Health, 0.f);
	return true;
}

#endif
