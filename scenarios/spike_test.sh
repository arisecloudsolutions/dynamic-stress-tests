#!/bin/bash
# Spike Test Scenario
# Simulates sudden traffic spikes to test system resilience

echo "🚀 SPIKE TEST SCENARIO"
echo "Simulating sudden traffic spike..."
echo "This tests how your API handles sudden load increases"
echo

# Ensure we have the basic config
if [ ! -f .env ]; then
    echo "❌ No .env file found. Copy from examples/ first:"
    echo "   cp examples/.env.petstore .env"
    exit 1
fi

# Load current config
source .env

# Spike test parameters
SPIKE_USERS=${SPIKE_USERS:-100}
SPIKE_RATE=${SPIKE_RATE:-50}
SPIKE_DURATION=${SPIKE_DURATION:-2m}

echo "📊 Spike Test Configuration:"
echo "   Target Users: $SPIKE_USERS"
echo "   Spawn Rate: $SPIKE_RATE users/second"
echo "   Duration: $SPIKE_DURATION"
echo "   Target API: $BASE_URL"
echo

read -p "🔥 Ready to start spike test? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Spike test cancelled."
    exit 0
fi

echo "⚡ Starting spike test..."

# Run the spike test
MAX_USERS=$SPIKE_USERS \
SPAWN_RATE=$SPIKE_RATE \
RUN_TIME=$SPIKE_DURATION \
docker compose run --rm locust

echo
echo "📊 Spike test completed!"
echo "Check reports/ directory for detailed results"
echo "Look for:"
echo "  - Response time spikes"
echo "  - Error rate increases"
echo "  - System recovery time"