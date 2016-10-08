function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}

var roomID = getUrlVars()["id"];
var server = "http://localhost:5000";
$(document).ready(function(){
	$("#emailInput").focus();
	$(document).keypress(function(e){
		if (e.which == 13){
			var email = $("#emailInput").val();
			$.get(server + "/joinRoom?idRoom="+roomID+"&email="+email,function(data){
				serverRepply=JSON.parse(data);
				var userID = serverRepply.id;
				startQuestions(userID,roomID);
				$(document).off("keypress");
			});
		}
	});
});

function startQuestions(userID, roomID){
	$("#emailContainer").fadeOut();

	var questions;

	$("#questionContainer").fadeIn();
	$.get(server+"/getRoomQuestion?idRoom="+roomID+"&idUser="+userID, function(data){
		serverRepply=JSON.parse(data);
		questions=serverRepply.questions;
		var answers=[];
		setQuestions(userID,roomID,questions,answers,0);
	});
}

function setQuestions(userID,roomID,questions,answers,i){
	$("#answerInput").val("").focus();
	if (i==questions.length){
		$.post(server+"/postRoomAnswers",{
			idRoom:roomID,
			idUser:userID,
			answers:answers
		});
		alert(answers[0].text);
		alert(answers[1].text);
	}
	else{
		$("#questionText").text(questions[i].text);
		$(document).keypress(function(e){
			if (e.which==13){
				answers[i]={
					id:questions[i].id,
					text:$("#answerInput").val()
				};
				$(document).off("keypress");
				setQuestions(userID,roomID,questions,answers,i+1);
			}
		});
	}
}