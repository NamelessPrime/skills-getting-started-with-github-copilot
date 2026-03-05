import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting between tests
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for varsity and JV players",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and participate in friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["jessica@mergington.edu", "ryan@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and creative visual arts",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in plays and musicals throughout the year",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["noah@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore STEM concepts",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["avery@mergington.edu", "grace@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to initial state before each test"""
    activities.clear()
    activities.update(INITIAL_ACTIVITIES)
    yield

client = TestClient(app)

def test_get_activities():
    """Test GET /activities returns all activities with correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have activities
    assert len(data) > 0
    assert "Chess Club" in data
    
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    activities_data = response.json()
    assert email in activities_data[activity]["participants"]

def test_signup_duplicate():
    """Test that signing up twice for the same activity fails"""
    email = "dupstudent@mergington.edu"
    activity = "Chess Club"
    
    # First signup should succeed
    response1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response2.status_code == 400
    
    data = response2.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    email = "test@mergington.edu"
    activity = "NonExistent Activity"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """Test successful unregistration from an activity"""
    email = "unregstudent@mergington.edu"
    activity = "Chess Club"
    
    # First sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the participant was removed
    response = client.get("/activities")
    activities_data = response.json()
    assert email not in activities_data[activity]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering a student who is not signed up"""
    email = "notsigned@mergington.edu"
    activity = "Chess Club"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity():
    """Test unregister from non-existent activity"""
    email = "test@mergington.edu"
    activity = "NonExistent Activity"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test that root path redirects to static index"""
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]