#!/bin/bash
# Soak Test Scenario
# Long-duration test to detect memory leaks and performance degradation

echo "🛁 SOAK TEST SCENARIO"
echo "Running extended duration test to detect memory leaks..."
echo "This helps identify performance degradation over time"
echo

# Ensure we have the basic config
if [ ! -f .env ]; then
    echo "❌ No .env file found. Copy from examples/ first:"
    echo "   cp examples/.env.petstore .env"
    exit 1
fi

# Load current config
source .env

# Soak test parameters
SOAK_USERS=${SOAK_USERS:-20}
SOAK_RATE=${SOAK_RATE:-2}
SOAK_DURATION=${SOAK_DURATION:-30m}

echo "📊 Soak Test Configuration:"
echo "   Concurrent Users: $SOAK_USERS"
echo "   Spawn Rate: $SOAK_RATE users/second"
echo "   Duration: $SOAK_DURATION"
echo "   Target API: $BASE_URL"
echo

echo "⏰ This test will run for $SOAK_DURATION"
echo "   Monitor these metrics during the test:"
echo "   - Memory usage trends"
echo "   - Response time degradation"
echo "   - Error rate increases"
echo "   - CPU usage patterns"
echo

read -p "🛁 Ready to start soak test? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Soak test cancelled."
    exit 0
fi

echo "🏊 Starting soak test..."
echo "💡 Tip: Monitor your system resources in another terminal"

# Run the soak test
MAX_USERS=$SOAK_USERS \
SPAWN_RATE=$SOAK_RATE \
RUN_TIME=$SOAK_DURATION \
docker compose run --rm locust

echo
echo "📊 Soak test completed!"
echo "Check reports/ directory for detailed results"
echo "Analyze for:"
echo "  - Response time trends over time"
echo "  - Memory usage patterns"
echo "  - Any error rate increases"
echo "  - Performance stability"