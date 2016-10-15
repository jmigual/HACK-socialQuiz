function getUrlVars() {
    var vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        console.log(m, key, value);
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}

// Regular expression to always match the proper server
var server = window.location.href.replace(/[?&]+.*/g, "").replace(/\/$/g, "");

// To encode URI
function encodeURI(jsonData) {
    var ret = ["?"];
    for (var d in jsonData) {
        ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(jsonData[d]));
    }
    return ret.join("&");
}

// Useful to get a json already parsed, if the third argument is given the query is encoded with encodeURI
function getJson(urlQuery, callback, jsonData) {
    if (arguments.length == 3) {
        urlQuery += encodeURI(jsonData);
    }
    $.get(urlQuery, function (data) {
        callback(JSON.parse(data));
    });
}

// To get a json from the server
function getServerJson(urlQuery, callback, jsonData) {
    getJson(server + urlQuery, callback, jsonData);
}

function createButton() {
    var b = document.createElement("button");
    $(b).attr("type", "button");
    $(b).addClass("btn btn-default");
    return b;
}

var urlVars = getUrlVars();
var hasError = false;
if ("id" in urlVars) {
    getServerJson("/room_status", function (reply) {
        switch (reply.status) {
            case "started":
            case "waiting":
                break;
            default:
                hasError = true;
        }
    }, {"room_id": urlVars["id"]});
}

$(document).ready(function () {
    var emailInput = $("#emailInput");
    if (hasError) {
        $("#emailContainer").hide();
        $("#errorContainer").show();
        return;
    } else {
        emailInput.focus();
    }
    emailInput.keypress(function (e) {
        if (e.which != 13) return;
        var emailInput = $("#emailInput");
        var email = emailInput.val();
        emailInput.fadeOut();
        getServerJson("/get_user_id", function (json) {
            var userID = json.id;
            emailInput.off("keypress");
            endEmail(userID, email);
        }, {"email": email});
    });
});

function endEmail(userID, email) {
    $("#emailContainer").fadeOut();
    urlVars = getUrlVars();
    if ("id" in urlVars) {
        var roomID = urlVars["id"];
        $.get(`${server}/join_room?${encodeURI({"id_room": roomID, "email": email})}`);

        getServerJson("/room_status", function (reply) {
            if (reply.status == "waiting") {
                startQuestions(userID, roomID)
            }
            else {
                $("#quizQuestionContainer").fadeIn();
                startQuiz(userID, roomID)
            }
        }, {"room_id": roomID});
    }
    else {
        startAdmin(userID);
    }
}

function startQuestions(userID, roomID) {
    $("#questionContainer").fadeIn();

    //shitty way to do this
    getServerJson("/get_room_questions", function (reply) {
        var questions = reply.questions;
        var answers = [];
        setQuestions(userID, roomID, questions, answers, 0);
    }, {"room_id": roomID});
}

function setQuestions(userID, roomID, questions, answers, i) {
    $("#answerInput").val("").focus();
    if (i == questions.length) {
        $.ajax({
            url: server + "/post_room_answers",
            data: JSON.stringify({
                "room_id": roomID,
                "user_id": userID,
                "answers": answers
            }),
            contentType: "application/json; charset=utf-8",
            type: "POST"
        });
        $("#questionContainer").fadeOut();
        $("#thanksContainer").fadeIn();
    }
    else {
        $("#questionText").text(questions[i].text);
        $(document).keypress(function (e) {
            if (e.which == 13) {
                answers[i] = {
                    id: questions[i].id,
                    text: $("#answerInput").val()
                };
                $(document).off("keypress");
                setQuestions(userID, roomID, questions, answers, i + 1);
            }
        });
    }
}

function startAdmin(userID) {
    $("#adminContainer").fadeIn();
    var nRoom = $("#newRoom");
    nRoom.off("click");
    nRoom.click(function () {
        newRoom(userID)
    });
    $("#checkboxContainer").empty();

    getServerJson("/get_rooms", function (rooms) {
        //console.log(rooms);
        for (var i in rooms) {
            var r = rooms[i];

            var text;
            if (r.status == "waiting") text = "START";
            else if (r.status == "started") text = "FINISH";
            else if (r.status == "finished") text = "FINISHED";
            var par = document.createElement("p");
            $(par).html(`Room #<b>${r.id}</b> status: ${r.status}`);
            $(par).css({"display": "inline", "color": "white"});

            var button = '';
            if (r.status != 'finished') {
                button = createButton();
                $(button).attr('id', "RoomButton" + r.id);
                $(button).attr('dbid', r.id);
                $(button).attr('status', r.status);
                $(button).html(text);
            }


            $("#checkboxContainer").append(par, button, '<br>');
            $(button).click(function () {
                var roomId = $(this).attr("dbid");
                var status = $(this).attr('status');
                if (status == "waiting") {
                    $.get(server + `/openRoom?id=${roomId}`, function () {
                        startAdmin(userID);
                    });
                } else if (status == "started") {
                    getServerJson("/finish_room", function (reply) {
                        var ranking = reply.ranking;
                        console.log(ranking);

                        var text = "<table class='table table-striped'><thead><tr><th>Name</th><th>Score</th></tr></thead><tbody>";
                        $.each(ranking, function (i, value) {
                            text = text + `<tr><td>${value.email}</td><td>${value.correct}</td></tr>`;
                        });
                        text = text + "</tbody></table>";
                        $("#modal-title").text("Ranking");
                        $("#urlModalText").html(text);
                        $("#urlModal").modal();
                        startAdmin(userID);
                    }, {"room_id": roomId});
                }
                $(this).off("click");
            });
        }
    }, {"user_id": userID});
}

function newRoom(userID) {
    $("#adminContainer").fadeOut();
    $("#newRoomContainer").fadeIn();
    var newQuestions = [];

    var questionInput = $("#questionInput");
    questionInput.keypress(function (e) {
        if (e.which != 13)  return;
        newQuestions.push(questionInput.val());
        questionInput.val("");
    });

    var finishRoom = $("#finishRoom");
    finishRoom.click(function () {
        getServerJson("/create_room", function (reply) {
            var roomID = reply.id;
            $.ajax({
                url: server + "/fill_room",
                data: JSON.stringify({
                    room_id: roomID,
                    question: newQuestions
                }),
                contentType: "application/json; charset=utf-8",
                type: "POST"
            });

            $("#questionInput").val("");
            questionInput.off("keypress");
            finishRoom.off("click");
            $("#cancelRoom").off("click");
            $("#newRoomContainer").fadeOut();
            startAdmin(userID);
            //alert(roomID);

            var link = window.location.href + "?id=" + roomID;

            $("#modal-title").text("Generated URL");
            $("#urlModalText").html("<a href='" + link + "'>" + link + "</a>");
            $("#urlModal").modal();
        }, {user_id: userID});
    });
    $("#cancelRoom").click(function () {
        $("#questionInput").val("");
        $(document).off("keypress");
        $("#finishRoom").off("click");
        $("#cancelRoom").off("click");
        $("#newRoomContainer").fadeOut();
        $("#adminContainer").fadeIn();
    });

}

function startQuiz(userID, roomID) {
    getServerJson("/get_quiz_question", function (serverReply) {
        if (serverReply.error != null) {
            $("#quizQuestionText").text(serverReply.error);
            console.log("Error: " + serverReply.error);
            return;
        }

        var quizQuestionID = serverReply.id;
        var quizAnswers = serverReply.answers;
        $("#quizQuestionText").text(serverReply.question);
        $.each(quizAnswers, function (i, value) {
            var button = createButton();
            $(button).attr("id", "answerButton" + value.id);
            $(button).text(value.text);
            $(button).css({width: "100%"});
            $("#quizAnswerColumn").append(button);
            $("#answerButton" + value.id).click(function () {
                answerQuiz(quizQuestionID, value.id, userID, roomID)
            });
        });
    }, {room_id: roomID, user_id: userID});
}

function answerQuiz(questionID, answerID, userID, roomID) {
    $("#quizAnswerColumn").empty();
    getServerJson("post_quiz_answer", function (serverReply) {
        console.log(serverReply);
        if (serverReply.correct) {
            alert("Correct answer");
        }
        else {
            alert("Incorrect answer\n the right answer was: " + serverReply.correctAnswer.text);
        }
        startQuiz(userID, roomID);
    }, {quiz_question_id: questionID, quiz_answer_id: answerID});
}