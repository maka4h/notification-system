import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime
import uuid

import nats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("event-generator")

# Environment variables
NATS_URL = os.environ.get("NATS_URL", "nats://nats:4222")
CONFIG_FILE = os.environ.get("CONFIG_FILE", "/app/config.json")

def load_config():
    """Load configuration from JSON file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {CONFIG_FILE}")
        logger.info(f"Found {len(config.get('hierarchical_paths', []))} paths, {len(config.get('event_types', []))} event types, {len(config.get('users', []))} users")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {CONFIG_FILE}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return None

# Load configuration
config = load_config()
if not config:
    logger.error("Failed to load configuration. Exiting.")
    exit(1)

# Extract configuration values
HIERARCHICAL_PATHS = config.get("hierarchical_paths", [])
EVENT_TYPES = config.get("event_types", [])
USERS = config.get("users", [])
GENERATE_INTERVAL = config.get("settings", {}).get("generate_interval", 5)

async def generate_random_event(nc):
    """Generate a random event and publish it to NATS"""
    # Pick random path and event type
    object_path = random.choice(HIERARCHICAL_PATHS)
    event_type = random.choice(EVENT_TYPES)
    user = random.choice(USERS)
    
    # Create path components for the subject
    path_components = object_path.strip('/').split('/')
    
    # Build the event data
    data = {
        "user_id": user["id"],
        "user_name": user["name"],
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Add event-specific data
    if event_type == "commented":
        comments = [
            "This looks great!",
            "I have some concerns about this approach.",
            "Can we discuss this in the next meeting?",
            "I've made some changes, please review.",
            "Let's get this finished by Friday."
        ]
        data["comment"] = random.choice(comments)
    
    elif event_type == "status_changed":
        statuses = ["in_progress", "on_hold", "completed", "blocked", "in_review"]
        data["old_status"] = random.choice(statuses)
        data["new_status"] = random.choice([s for s in statuses if s != data["old_status"]])
    
    elif event_type == "assigned":
        assignee = random.choice([u for u in USERS if u["id"] != user["id"]])
        data["assignee_id"] = assignee["id"]
        data["assignee_name"] = assignee["name"]
    
    # Build the full event payload
    payload = {
        "id": str(uuid.uuid4()),
        "object_path": object_path,
        "event_type": event_type,
        "timestamp": data["timestamp"],
        "data": data
    }
    
    # Publish to NATS
    subject = f"app.events.{'.'.join(path_components)}.{event_type}"
    await nc.publish(subject, json.dumps(payload).encode())
    
    logger.info(f"Published event: {subject}")
    logger.debug(f"Event payload: {payload}")
    
    return subject, payload

async def run_generator():
    # Connect to NATS
    nc = await nats.connect(servers=[NATS_URL])
    js = nc.jetstream()
    
    logger.info(f"Connected to NATS at {NATS_URL}")
    
    # Ensure the EVENTS stream exists
    try:
        await js.add_stream(name="EVENTS", subjects=["app.events.>"])
        logger.info("Created EVENTS stream")
    except Exception as e:
        logger.info(f"Stream already exists or error: {e}")
    
    # Generate events periodically
    try:
        # Generate initial set of events
        settings = config.get("settings", {}) if config else {}
        initial_events = settings.get("initial_events", 10)
        logger.info(f"Generating {initial_events} initial events...")
        for _ in range(initial_events):
            await generate_random_event(nc)
        
        # Generate events periodically
        while True:
            await asyncio.sleep(GENERATE_INTERVAL)
            await generate_random_event(nc)
    except Exception as e:
        logger.exception(f"Error generating events: {e}")
    finally:
        await nc.close()

if __name__ == "__main__":
    logger.info("Starting event generator")
    asyncio.run(run_generator())
