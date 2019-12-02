function showHidePass() {
  let x = document.querySelector("#passForm");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}


let loadUsers = function () {
  console.log("loadUsers");
  // request the data from the server:
  fetch("http://localhost:8080/users", {
    method: "GET",
    credentials: "include"
  }).then(function (response) {
    // parse (unpackage) the data from the server:
    response.json().then(function (data) {
      let usersList = document.querySelector("#users");
      usersList.innerHTML = "";

      data.forEach(function (user) {
        let row = document.createElement("div");
        row.className += "row my-3";

        let dataCol = document.createElement("div");
        dataCol.className += "col";

        let nameHeading = document.createElement("h3");
        nameHeading.innerHTML = user.firstname + " "  + user.lastname;
        dataCol.appendChild(nameHeading);

        let emailDiv = document.createElement("div");
        emailDiv.innerHTML = user.email;
        dataCol.appendChild(emailDiv);

        let phoneDiv = document.createElement("div");
        phoneDiv.innerHTML = user.phone;
        dataCol.appendChild(phoneDiv);

        let passHashDiv = document.createElement("div");
        passHashDiv.innerHTML = user.passHash.slice(30, 55);
        passHashDiv.setAttribute("class", "text-truncate");
        dataCol.appendChild(passHashDiv);
        row.appendChild(dataCol);

        let updateBtnCol = document.createElement("div");
        updateBtnCol.className += "col-2 col-md-3";

        let updateButton = document.createElement("button");
        updateButton.className += "btn btn-info";
        updateButton.innerHTML = "Update";
        updateButton.onclick = function () {
          getUser(user.id);
        };
        updateBtnCol.appendChild(updateButton);

        row.appendChild(updateBtnCol);


        let delBtnCol = document.createElement("div");
        delBtnCol.className += "col-2 col-md-3";

        let deleteButton = document.createElement("button");
        deleteButton.className += "btn btn-danger";
        deleteButton.setAttribute("data-toggldeletee", "modal");
        deleteButton.setAttribute("data-target", "#deleteModal");
        deleteButton.innerHTML = "Delete";
        deleteButton.onclick = function () {
          if (confirm("Are you sure you want to delete " + user.firstname + "?")) {
            deleteUser(user.id);
            loadUsers();
          }
        };
        delBtnCol.appendChild(deleteButton);
        row.appendChild(delBtnCol);


        //col.appendChild(deleteDiv);
        //col.appendChild(deleteButton);

        usersList.appendChild(row);
      });
      
    });
  });
};

function deleteUser(userID) {
  fetch("http://localhost:8080/users/" + userID, {
    method: 'DELETE',
    credentials: "include",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then(loadUsers);
}

function getUser(userID) {
  console.log("get user");
  //let idField = document.querySelector('#edit-id');
  //idField.value = userID;
  fetch("http://localhost:8080/users/" + userID, {
    method: "GET",
    credentials: "include",
  }).then(function (response) {
    response.json().then(function (data) {
      let editID = document.querySelector("#edit-id");
      let editEmail = document.querySelector("#edit-email");
      let editFName = document.querySelector("#edit-firstName");
      let editLName = document.querySelector("#edit-lastName");
      let editPhone = document.querySelector("#edit-phone");

      // prefill textboxes with selected user data
      editID.value = data.id;
      editEmail.value = data.email;
      editFName.value = data.firstname;
      editLName.value = data.lastname;
      editPhone.value = data.phone;
  });
});}

let hideShowPass = document.querySelector('#hideShowPass');
hideShowPass.addEventListener('change', function(event) {
  let password = document.querySelector('#password');
  if (password.type === 'password') {
    password.type = 'text';
  } else {
    password.type = 'password';
  }
});


document.addEventListener('submit', function(event) {
  if (!event.target.matches('#createUserForm')) return;
  event.preventDefault();  // don't follow the link

  let elements = document.querySelector('#createUserForm').elements;
  let inputs = {
      "firstName": elements.firstName.value,
      "lastName": elements.lastName.value,
      "email": elements.email.value,
      "password": elements.password.value,
      "phone":elements.phone.value
  };
  let body = "";

  // create a URL-encoded string from form inputs
  Object.keys(inputs).forEach(function (key, i) {
    body += key + "=" + encodeURIComponent(inputs[key]);
    if (i < Object.keys(inputs).length - 1) {
      body += "&";
    }
  });

  fetch('http://localhost:8080/users', {
    method: 'POST',
    body: body,
    credentials: "include",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then(function(response) {
    let signupResponse = document.querySelector("#signup-response");
    if (response.status === 409) {
      signupResponse.innerHTML = "That email is unavailable";
      signupResponse.style.color = "#c94747";
    } else if (response.status === 201) {
      signupResponse.innerHTML = "Account created successfully";
      signupResponse.style.color = "#439c47";
      loadUsers();
    }
  });
});

document.addEventListener('submit', function(event) {
  if (!event.target.matches('#updateUserForm')) return;
  event.preventDefault();  // don't follow the link

  console.log("update user");
  let elements = document.getElementById("updateUserForm").elements;

  let inputs = {
      "id": elements["edit-id"].value,
      "email": elements["edit-email"].value,
      "password": elements["edit-password"].value,
      "firstName": elements["edit-firstName"].value,
      "lastName": elements["edit-lastName"].value,
      "phone": elements["edit-phone"].value
  };
  let body = "";

  Object.keys(inputs).forEach(function (key, i) {
    body += key + "=" + encodeURIComponent(inputs[key]);
    if (i < Object.keys(inputs).length - 1) {
      body += "&";
    }
  });

  fetch('http://localhost:8080/users/' + inputs.id, {
    method: 'PUT',
    body: body,
    credentials: "include",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then(loadUsers);
});

// sign in
document.addEventListener("submit", function(event) {
  if (!event.target.matches("#signin-form")) return;
  event.preventDefault();  // don't follow the link

  let email = document.querySelector("#signin-email").value; 
  let password = document.querySelector("#signin-password").value;
  email = encodeURIComponent(email);
  password = encodeURIComponent(password);
  let body = "email=" + email + "&password=" + password;

  fetch('http://localhost:8080/sessions', {
    method: 'POST',
    body: body,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then(function(response) {
      if (response.status === 200) {
        loadUsers();
        let elements = document.getElementsByClassName("restricted");

        for (let element of elements) {
          element.style.visibility = "visible";
        }
  
        let signinResponse = document.querySelector("#signin-response");
        signinResponse.innerHTML = "Success";
        signinResponse.style.color = "#439c47";
      } else if (response.status === 401) {
        let signinResponse = document.querySelector("#signin-response");
        signinResponse.innerHTML = "The email or password was incorrect";
        signinResponse.style.color = "#c94747";
      }
  });
});

// check if email is valid during signup - live
const email = document.querySelector("#email");
email.addEventListener("blur", (event) => {
  const emailAttempt = email.value;
  if (emailAttempt == "") return;

  fetch('http://localhost:8080/tools/' + emailAttempt, {
    method: 'POST',
    credentials: "include",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then(function(response) {
    if (response.status === 409) {
      const emailForm = document.querySelector("#email");
      emailForm.style.borderColor = "#c94747";
      const emailResponse = document.querySelector("#invalid-email");
      emailResponse.innerHTML = "That email is unavailable";
      emailResponse.style.color = "#c94747";
    } else {
      const emailForm = document.querySelector("#email");
      emailForm.style.borderColor = "#439c47";
      const emailResponse = document.querySelector("#invalid-email");
      emailResponse.innerHTML = "";
    }
  });
});


function checkSession () {
  fetch("http://localhost:8080/sessions", {
    method: "GET",
    credentials: "include"})
    .then(function (response) {
      if (response.status == 200) {
        console.log("logged in");
        let elements = document.getElementsByClassName("restricted");

        for (let element of elements) {
          element.style.visibility = "visible";
        }
        loadUsers();
        //refreshFavorites();

/*
        response.json().then(function (data) {
          userInfo = data;
          document.querySelector("#name").innerHTML = "Welcome " + userInfo;

      });
*/
      } else {
        //loginModal.style.display = "block";
        console.log("not logged in");
      }
  });
}

// run at page load to check if user is logged in
checkSession();


/*

fetch("http://localhost:8080/users", {
  credentials: "include"
}).then(function (response) {
  response.json().then(function (data) {

  }
})





*/