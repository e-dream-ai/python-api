import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client
from edream_sdk.types.playlist_types import CreatePlaylistRequest

# Load environment variables from .env file
load_dotenv()

# Constants
BACKEND_URL = "https://api-stage.infinidream.ai/api/v1"
TEST_PLAYLIST_UUID = ""
TEST_DESCRIPTION = "This description was added via Python SDK!"


def get_api_key() -> Optional[str]:
    """Retrieve and validate API key from environment variables."""
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        print("ERROR: No API key found. Please check your .env file.")
        return None
    return api_key


def create_client(api_key: str):
    """Create and return an eDream client instance."""
    return create_edream_client(
        backend_url=BACKEND_URL,
        api_key=api_key
    )


def test_user_connection(client) -> bool:
    """Test basic connection by getting logged user info."""
    try:
        user = client.get_logged_user()
        print(f"Connected as: {user['name']}")
        return True
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return False


def test_playlist_operations(client, playlist_uuid: str) -> None:
    """Test playlist retrieval and update operations."""
    try:
        # Get existing playlist
        playlist = client.get_playlist(playlist_uuid)
        print(f"Current playlist: {playlist['name']}")
        print(f"Current description: {playlist.get('description', 'No description')}")
        
        # Update playlist with description
        update_data = {
            "name": playlist['name'],
            "description": TEST_DESCRIPTION
        }
        
        updated_playlist = client.update_playlist(playlist_uuid, update_data)
        print(f"Updated playlist description: {updated_playlist.get('description')}")
        
    except Exception as e:
        print(f"Error during playlist operations: {e}")


def test_create_playlist(client) -> Optional[str]:
    """Test playlist creation functionality."""
    try:
        basic_playlist_data: CreatePlaylistRequest = {
            "name": f"Test Playlist {int(time.time())}"
        }
        
        print("Creating basic playlist...")
        basic_playlist = client.create_playlist(basic_playlist_data)
        print(f"✓ Created basic playlist: {basic_playlist['name']} (UUID: {basic_playlist['uuid']})")
        
        detailed_playlist_data: CreatePlaylistRequest = {
            "name": f"Detailed Test Playlist {int(time.time())}",
            "description": "This is a test playlist created via Python SDK with full details",
            "nsfw": False
        }
        
        print("Creating detailed playlist...")
        detailed_playlist = client.create_playlist(detailed_playlist_data)
        print(f"  Created detailed playlist: {detailed_playlist['name']} (UUID: {detailed_playlist['uuid']})")
        print(f"  Description: {detailed_playlist.get('description', 'No description')}")
        print(f"  NSFW: {detailed_playlist.get('nsfw', 'Not set')}")
        
        nsfw_playlist_data: CreatePlaylistRequest = {
            "name": f"NSFW Test Playlist {int(time.time())}",
            "description": "This is an NSFW test playlist",
            "nsfw": True
        }
        
        print("Creating NSFW playlist...")
        nsfw_playlist = client.create_playlist(nsfw_playlist_data)
        print(f"✓ Created NSFW playlist: {nsfw_playlist['name']} (UUID: {nsfw_playlist['uuid']})")
        print(f"  NSFW flag: {nsfw_playlist.get('nsfw', 'Not set')}")
        
        return basic_playlist['uuid']
        
    except Exception as e:
        print(f"✗ Error during playlist creation: {e}")
        return None


def test_create_and_update_playlist(client) -> None:
    """Test creating a playlist and then updating it."""
    try:
        create_data: CreatePlaylistRequest = {
            "name": f"Create-Update Test {int(time.time())}",
            "description": "Initial description"
        }
        
        print("Creating playlist for update test...")
        playlist = client.create_playlist(create_data)
        playlist_uuid = playlist['uuid']
        print(f"✓ Created playlist for testing: {playlist['name']}")
        
        update_data = {
            "name": f"Updated {playlist['name']}",
            "description": "Updated description via Python SDK"
        }
        
        print("Updating the created playlist...")
        updated_playlist = client.update_playlist(playlist_uuid, update_data)
        print(f"✓ Updated playlist: {updated_playlist['name']}")
        print(f"  New description: {updated_playlist.get('description')}")
        
    except Exception as e:
        print(f"✗ Error during create-update test: {e}")


def test_playlist_edge_cases(client) -> None:
    """Test edge cases for playlist creation."""
    try:
        print("Testing edge cases...")
        
        empty_desc_data: CreatePlaylistRequest = {
            "name": f"Empty Description Test {int(time.time())}",
            "description": ""
        }
        
        empty_desc_playlist = client.create_playlist(empty_desc_data)
        print(f"✓ Created playlist with empty description: {empty_desc_playlist['name']}")
        
        # Test playlist with long name
        long_name_data: CreatePlaylistRequest = {
            "name": f"Very Long Playlist Name Test That Should Still Work Fine {int(time.time())}"
        }
        
        long_name_playlist = client.create_playlist(long_name_data)
        print(f"✓ Created playlist with long name: {long_name_playlist['name'][:50]}...")
        
        # Test playlist with only required field
        minimal_data: CreatePlaylistRequest = {
            "name": f"Minimal Test {int(time.time())}"
        }
        
        minimal_playlist = client.create_playlist(minimal_data)
        print(f"✓ Created minimal playlist: {minimal_playlist['name']}")
        
    except Exception as e:
        print(f"✗ Error during edge case testing: {e}")


def test_playlist_description() -> None:
    """Test the existing playlist description functionality."""
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    # Create client
    client = create_client(api_key)
    
    # Test connection
    if not test_user_connection(client):
        return
    
    # Test playlist operations
    test_playlist_operations(client, TEST_PLAYLIST_UUID)


def test_comprehensive_playlist_functionality() -> None:
    """Test all playlist functionality including creation."""
    print("=" * 60)
    print("COMPREHENSIVE PLAYLIST FUNCTIONALITY TESTS")
    print("=" * 60)
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    # Create client
    client = create_client(api_key)
    
    # Test connection
    print("\n1. Testing connection...")
    if not test_user_connection(client):
        return
    
    print("\n2. Testing playlist creation...")
    created_playlist_uuid = test_create_playlist(client)
    
    print("\n3. Testing create and update workflow...")
    test_create_and_update_playlist(client)
    
    print("\n4. Testing edge cases...")
    test_playlist_edge_cases(client)
    
    if created_playlist_uuid:
        print(f"\n5. Testing operations on created playlist...")
        test_playlist_operations(client, created_playlist_uuid)
    
    print("\n6. Testing operations on existing playlist...")
    test_playlist_operations(client, TEST_PLAYLIST_UUID)
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_comprehensive_playlist_functionality()
    