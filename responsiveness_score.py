"""
AI Agent Responsiveness Score Calculator
Author: Deeptanshu Sankhwar (GitHub: @Deeptanshu-sankhwar)
Date: 2025-02-24
Description: Computes a responsiveness score (0-100) for AI agents based on their Twitter engagement, impressions, follower growth, and other relevant metrics.
"""

import json
import numpy as np

JSON_FILE = "scraped_data.json" 
OUTPUT_JSON_FILE = "normalised_responsiveness_score_data.json"
OUTPUT_PNG_FILE = "responsiveness_graph.png"

def safe_div(numerator, denominator, default=0):
    """
    Safely divide two numbers, avoiding division by zero.
    """
    return numerator / denominator if denominator > 1e-6 else default

def compute_responsiveness_score(agent_data):
    """
    Compute the responsiveness score (0-100) for an AI agent based on Twitter engagement metrics.
    """
    try:
        # Extract agent metadata
        agent_name = agent_data.get("agentDetails", {}).get("name", "Unknown Agent")
        twitter_usernames = agent_data.get("agentDetails", {}).get("twitterUsernames", [])
        profile_image_url = agent_data.get("profileImageUrl", "")

        # Extract Twitter data safely
        twitter_now = agent_data.get("twitterStats", {}).get("dataPoints", {}).get("Now", {})
        twitter_7_days_ago = agent_data.get("twitterStats", {}).get("dataPoints", {}).get("_7DaysAgo", {})

        # Engagement Rate (ER) = Engagements Count / Impressions Count
        engagements = twitter_7_days_ago.get("engagementsCount", {}).get("value", 0)
        impressions = twitter_7_days_ago.get("impressionsCount", {}).get("value", 1e-6)  # Avoid division by zero
        ER = safe_div(engagements, impressions)

        # Smart Engagement Points per follower (SEP) = Smart Engagement Points / Followers
        smart_engagement_points = twitter_7_days_ago.get("smartEngagementPoints", {}).get("value", 0)
        followers = twitter_now.get("followersCount", {}).get("value", 1e-6)  # Avoid division by zero
        SEP = safe_div(smart_engagement_points, followers)

        # Follower Growth Rate (FGR) = (Current Followers - Followers 7 Days Ago) / Followers 7 Days Ago
        prev_followers = twitter_7_days_ago.get("followersCount", {}).get("value", 1e-6)
        FGR = safe_div(followers - prev_followers, prev_followers)

        # Mindshare (MS) - normalized with similar projects, handle missing `valueForSimilarProjects`
        mindshare = twitter_7_days_ago.get("mindshare", {}).get("value", 0)
        avg_mindshare = twitter_7_days_ago.get("mindshare", {}).get("valueForSimilarProjects", 1e-6)  # Avoid division by zero
        MS = safe_div(mindshare, avg_mindshare)

        # Best Tweet Impact (BTI) - average engagements per best tweet
        best_tweets = twitter_7_days_ago.get("bestTweets", [])
        tweet_engagements = [int(tweet.get("item5", 0)) for tweet in best_tweets if "item5" in tweet]
        BTI = np.mean(tweet_engagements) if tweet_engagements else 0  # Avoid empty list issue

        # Define weights for each metric
        weights = {
            "ER": 0.3,   # Engagement Rate
            "SEP": 0.2,  # Smart Engagement per Follower
            "FGR": 0.2,  # Follower Growth Rate
            "MS": 0.2,   # Mindshare Impact
            "BTI": 0.1   # Best Tweet Impact
        }

        # Compute weighted sum
        raw_score = (
            weights["ER"] * ER +
            weights["SEP"] * SEP +
            weights["FGR"] * FGR +
            weights["MS"] * MS +
            weights["BTI"] * BTI
        )

        return {
            "name": agent_name,
            "twitterUsernames": twitter_usernames,
            "profileImageUrl": profile_image_url,
            "responsivenessScore": raw_score  
        }

    except Exception as e:
        print(f"Error computing responsiveness score for agent: {e}")
        return None

def normalize_and_sort_agents(agents):
    """
    Normalize responsiveness scores between 0-100, sort them in descending order, and return JSON output.
    """
    # Filter out None values
    valid_agents = [agent for agent in agents if agent and agent["responsivenessScore"] is not None]

    if not valid_agents:
        return []

    # Extract scores for normalization
    scores = [agent["responsivenessScore"] for agent in valid_agents]
    min_score = min(scores)
    max_score = max(scores)

    # Avoid division by zero if all scores are the same
    if min_score == max_score:
        for agent in valid_agents:
            agent["responsivenessScore"] = 50  # Assign neutral score of 50
    else:
        for agent in valid_agents:
            agent["responsivenessScore"] = 100 * (agent["responsivenessScore"] - min_score) / (max_score - min_score)

    # Sort agents by descending responsiveness score
    valid_agents.sort(key=lambda x: x["responsivenessScore"], reverse=True)

    return valid_agents

import matplotlib.pyplot as plt

def plot_responsiveness_graph(sorted_agents, limit):
    """
    Plot the top few agents in a graph in the order of their responsivenesss scores.
    """
    # Extract agent names and their scores
    agent_names = [agent["name"] for agent in sorted_agents[:limit]]
    scores = [agent["responsivenessScore"] for agent in sorted_agents[:limit]]

    # Plot the bar chart
    plt.figure(figsize=(12, 8))  
    plt.barh(agent_names[::-1], scores[::-1])
    plt.xlabel("Responsiveness Score", fontsize=12)
    plt.ylabel("AI Agents", fontsize=12)
    plt.title("Top {} Most Responsive AI Agents on Twitter".format(limit), fontsize=14)
    plt.xlim(0, 100)
    plt.grid(axis="x", linestyle="--", alpha=0.6)

    plt.yticks(fontsize=8)

    # Save the figure as PNG
    graph_path = OUTPUT_PNG_FILE
    plt.savefig(graph_path, dpi=300, bbox_inches="tight")
    plt.close()


# Load JSON data from file
with open(JSON_FILE, "r", encoding="utf-8") as file:
    agents_data = json.load(file)

# Compute scores for all agents
all_agents = [compute_responsiveness_score(agent) for agent in agents_data]

# Normalize and sort results
sorted_agents = normalize_and_sort_agents(all_agents)

# Save sorted JSON output
with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(sorted_agents, file, indent=4)

print(f"Sorted responsiveness scores saved to {OUTPUT_JSON_FILE}")

# Plot sorted agents in a graph
plot_responsiveness_graph(sorted_agents, 50)

print(f"Graph saved to {OUTPUT_PNG_FILE}")
