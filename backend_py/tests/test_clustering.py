from app.services.clustering.service import heat_score, trajectory


def test_heat_score_bounds():
    assert 0 <= heat_score(0, 0, 0) <= 100
    assert heat_score(0, 0, 0) >= 20
    assert heat_score(10, 1, 1) <= 100


def test_heat_score_increases_with_velocity():
    low = heat_score(1, 0, 0)
    high = heat_score(5, 0, 0)
    assert high >= low


def test_trajectory_heating():
    assert trajectory(30, 40) == "heating"
    assert trajectory(50, 56) == "heating"


def test_trajectory_cooling():
    assert trajectory(70, 60) == "cooling"
    assert trajectory(55, 49) == "cooling"


def test_trajectory_stable():
    assert trajectory(50, 52) == "stable"
    assert trajectory(50, 48) == "stable"
