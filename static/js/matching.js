
let users = [];
let currentIndex = 0;
let currentUserInterests = [];


document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("swipe-card")) {
        fetchRecommendations();
    }
});

function fetchRecommendations() {
    fetch("/api/recommendations")
        .then(response => response.json())
        .then(data => {
            users = data.users;
            currentUserInterests = data.current_user_interests;
            currentIndex = 0;
            showCurrentUser();
        })
        .catch(error => {
            console.error("Error fetching recommendations:", error);
        });
}


function showCurrentUser() {
    const card = document.getElementById("swipe-card");
    if (!card) return;

    if (currentIndex >= users.length) {
        card.innerHTML = "<p>No more users to show 🌱</p>";
        return;
    }

    const user = users[currentIndex];

    document.getElementById("user-name").innerText =
        user.name + ", " + user.age;

    document.getElementById("user-role").innerText =
        user.role;

    document.getElementById("match-badge").innerText =
        user.score + "% Match";

    
    let avatar = "🙂";

    if (user.role === "Youth" && user.gender === "Female") {
        avatar = "👱‍♀️";
    } else if (user.role === "Youth" && user.gender === "Male") {
        avatar = "👱";
    } else if (user.role === "Senior" && user.gender === "Female") {
        avatar = "🧑‍🦳";
    } else if (user.role === "Senior" && user.gender === "Male") {
        avatar = "👨‍🦳";
    }

    const avatarDiv = document.getElementById("user-avatar");
    if (avatarDiv) {
        avatarDiv.innerText = avatar;
    }


    const common = user.interests.filter(i =>
        currentUserInterests.includes(i)
    );

    const sharedTextDiv = document.getElementById("shared-text");

    if (common.length === 0) {
        sharedTextDiv.innerText =
            "You do not share any common interests yet.";
    } else {
        sharedTextDiv.innerText =
            "You both share " + common.length + " common interest(s):";
    }

    const tagsDiv = document.getElementById("interest-tags");
    tagsDiv.innerHTML = "";

    common.forEach(i => {
        const span = document.createElement("span");
        span.className = "tag";
        span.style.background = "#ffe8d1";
        span.style.color = "#d35400";
        span.innerText = i;
        tagsDiv.appendChild(span);
    });

    user.interests.forEach(i => {
        if (!common.includes(i)) {
            const span = document.createElement("span");
            span.className = "tag";
            span.innerText = i;
            tagsDiv.appendChild(span);
        }
    });

    document.getElementById("user-about").innerText =
        user.about;
}


function passCurrent() {
    currentIndex++;
    showCurrentUser();
}

function matchCurrent() {
    if (currentIndex >= users.length) return;

    const user = users[currentIndex];

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/match/" + user.id;

    document.body.appendChild(form);
    form.submit();
}


function handleRemove(button) {
    const removeUrl = button.dataset.removeUrl;

    if (!removeUrl) {
        alert("Remove URL not found on button.");
        return;
    }

    if (!confirm("Are you sure you want to remove this match?")) {
        return;
    }


    window.location.href = removeUrl;
}
