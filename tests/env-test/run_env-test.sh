echo "Running environment tests..."
echo "Running with Rendering"
python env-test.py --num_episodes=10 --seed=0 --render
echo "Running without Rendering"
python env-test.py --num_episodes=10 --seed=0