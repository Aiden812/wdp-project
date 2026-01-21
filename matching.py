from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from matching_model import calculate_similarity

matching_bp = Blueprint("matching", __name__)


#temporary in memory data
users = [
    {
        "id": "u1",
        "name": "Margaret Chen",
        "age": 68,
        "role": "Senior",
        "gender": "Female",
        "about": "Retired teacher who loves sharing traditional recipes and Singapore history.",
        "interests": ["Cooking", "History", "Gardening"]
    },
    {
        "id": "u2",
        "name": "Alex Tan",
        "age": 21,
        "role": "Youth",
        "gender": "Male",
        "about": "University student interested in technology and learning from seniors.",
        "interests": ["History", "Technology", "Cooking"]
    },
    {
        "id": "u3",
        "name": "Ryan Lim",
        "age": 23,
        "role": "Youth",
        "gender": "Male",
        "about": "Enjoys gaming and building apps in his free time.",
        "interests": ["Gaming", "Technology"]
    },
    {
        "id": "u4",
        "name": "Sarah Lim",
        "age": 25,
        "role": "Youth",
        "gender": "Female",
        "about": "Art lover who enjoys cooking and cultural activities.",
        "interests": ["Cooking", "Art", "History"]
    },
    {
        "id": "u5",
        "name": "David Ong",
        "age": 70,
        "role": "Senior",
        "gender": "Male",
        "about": "Former engineer who enjoys walking and gardening.",
        "interests": ["Gardening", "Walking", "History"]
    }
]


matches = []


CURRENT_USER_ID = "u1"   # Margaret Chen


#matching
@matching_bp.route("/matching")
def matching_page():
    return render_template("matching.html")



@matching_bp.route("/api/recommendations")
def get_recommendations_api():
    current_user = next(u for u in users if u["id"] == CURRENT_USER_ID)

    recommendations = []

    for user in users:
        if user["id"] == CURRENT_USER_ID:
            continue

  
        if current_user["role"] == "Senior" and user["role"] != "Youth":
            continue

        if current_user["role"] == "Youth" and user["role"] != "Senior":
            continue

        score = calculate_similarity(
            current_user["interests"],
            user["interests"]
        )

        recommendations.append({
            "id": user["id"],
            "name": user["name"],
            "age": user["age"],
            "role": user["role"],
            "gender": user["gender"],
            "about": user["about"],
            "interests": user["interests"],
            "score": score
        })

    return jsonify({
        "current_user_interests": current_user["interests"],
        "users": recommendations
    })


#no duplicates
@matching_bp.route("/match/<target_id>", methods=["POST"])
def create_match(target_id):
    for m in matches:
        if m["user_id"] == CURRENT_USER_ID and m["target_id"] == target_id:
            flash("You have already matched with this user.", "warning")
            return redirect(url_for("matching.matching_page"))

    matches.append({
        "user_id": CURRENT_USER_ID,
        "target_id": target_id
    })

    flash("Match successful!", "success")
    return redirect(url_for("matching.matching_page"))


#viewmatches
@matching_bp.route("/matches")
def view_matches():
    user_matches = []

    for m in matches:
        if m["user_id"] == CURRENT_USER_ID:
            target_user = next(u for u in users if u["id"] == m["target_id"])

            user_matches.append({
                "id": target_user["id"],
                "name": target_user["name"],
                "age": target_user["age"],
                "role": target_user["role"],
                "gender": target_user["gender"]
            })

    return render_template("matches.html", matches=user_matches)



@matching_bp.route("/match/remove/<target_id>")
def remove_match(target_id):
    global matches


    print("Removing match:", CURRENT_USER_ID, target_id)

    matches = [
        m for m in matches
        if not (m["user_id"] == CURRENT_USER_ID and m["target_id"] == target_id)
    ]

    flash("Match removed successfully.", "warning")
    return redirect(url_for("matching.view_matches"))
