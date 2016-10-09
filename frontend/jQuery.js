function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}


//var server = "http://interact.siliconpeople.net:5000"
var server = "http://localhost:5000";

var urlVars=getUrlVars();
var hasError = false;
if ("id" in urlVars){
	var roomID = urlVars["id"];
	$.get(server+"/statusRoom?id="+roomID,function(data){
		var serverReply=JSON.parse(data);
		switch (serverReply.status) {
			case "started":
			case "waiting":
				break;
			default:
				hasError = true;
		}
	});
}

$(document).ready(function(){
	var emailInput = $("#emailInput");
	if (hasError) {
		$("#emailContainer").hide();
		$("#errorContainer").show();
		return;
	} else {
		emailInput.focus();
	}
	emailInput.keypress(function(e) {
		if (e.which != 13) return;
		var emailInput = $("#emailInput");
		var email = emailInput.val();
		emailInput.fadeOut();
		$.get(server + "/getUserId?email="+email,function(data){
			var serverReply = JSON.parse(data);
			var userID = serverReply.id;
			emailInput.off("keypress");
			endEmail(userID, email);
		});
	});
});

function endEmail(userID,email){
	$("#emailContainer").fadeOut();
	urlVars=getUrlVars();
	if ("id" in urlVars){
		var roomID = urlVars["id"];
		$.get(server + "/joinRoom?idRoom="+roomID+"&email="+email);
		$.get(server+"/statusRoom?id="+roomID,function(data){
			serverRepply=JSON.parse(data);
			if (serverRepply.status== "waiting"){
				startQuestions(userID,roomID)
			}
			else{
				$("#quizQuestionContainer").fadeIn();
				startQuiz(userID,roomID)
			}
		});
	}
	else{
		startAdmin(userID);
	}
}

function startQuestions(userID, roomID){
	var questions;

	$("#questionContainer").fadeIn();
	//shitty way to do this
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
		$.ajax({
            url:server+"/postRoomAnswers",
            data:JSON.stringify({
				idRoom:roomID,
				idUser:userID,
				answers:answers
			}),
			contentType:"application/json; charset=utf-8",
			type:"POST"
		});
		$("#questionContainer").fadeOut();
		$("#thanksContainer").fadeIn();
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

function openRoom() {

}

function startAdmin(userID){
	$("#adminContainer").fadeIn();
	$("#newRoom").click(function(){newRoom(userID)});
	$("#checkboxContainer").empty();

	$.get(server+"/getRooms?userId="+userID, function(data){
		var rooms = JSON.parse(data);
		console.log(rooms);
		//for(var r in rooms) {
		for (var i in rooms) {
			var r = rooms[i];

			var text;
			if (r.status == "waiting") text = "START";
			else if (r.status == "started") text = "FINISH";
			else if (r.status == "finished") text = "FINISHED";
			var par = document.createElement("p");
			$(par).css("display: inline; color: white");
			$(par).html(`Room #<b>${r.id}</b>${text}`);

			var button = document.createElement("button");
            $(button).attr("type", "button");
            $(button).addClass("btn btn-default");
            $(button).attr('id', "RoomButton" + r.id);
            $(button).attr('dbid', r.id);
            $(button).attr('status', r.status);
            $(button).html(text);

			$("#checkboxContainer").append(par, button);
			$(button).click(function(){
				var id = $(this).attr("dbid");
                var status = $(this).attr('status');
                if (status == "waiting") {
                    $.get(server + `/openRoom?id=${id}`, function () {
                        startAdmin(userID);
                    });
                } else if (status == "started") {
                    $.get(server + `/finishRoom?id=${id}`, function (ranking) {
                        $("#urlModalText").html(ranking);
                        $("#urlModal").modal();
                        startAdmin(userID);
                    });
                }
				$(this).off("click");
			});
		}
	});
}

function newRoom(userID){
	$("#adminContainer").fadeOut();
	$("#newRoomContainer").fadeIn();
	var newQuestions = [];

	var questionInput = $("#questionInput");
	questionInput.keypress(function(e){
		if (e.which != 13)  return;
		newQuestions.push(questionInput.val());
		questionInput.val("");
	});

	var finishRoom = $("#finishRoom");
	finishRoom.click(function(){
		$.get(server+"/createRoom?userId="+userID,function(data){
			var serverReply = JSON.parse(data);
			var roomID = serverReply.id;
			$.ajax({
	            url:server+"/fillRoom",
	            data:JSON.stringify({
	            	id: roomID,
					question: newQuestions
				}),
				contentType:"application/json; charset=utf-8",
				type:"POST"
			});

			$("#questionInput").val("");
			questionInput.off("keypress");
			finishRoom.off("click");
			$("#cancelRoom").off("click");
			$("#newRoomContainer").fadeOut();
			$("#adminContainer").fadeIn();
			//alert(roomID);

			var link = window.location.href + "?id=" + roomID;
			$("#urlModalText").html("<a href='" + link + "'>" + link + "</a>");
			$("#urlModal").modal();
		});
	});
	$("#cancelRoom").click(function(){
			$("#questionInput").val("");
			$(document).off("keypress");
			$("#finishRoom").off("click");
			$("#cancelRoom").off("click");
			$("#newRoomContainer").fadeOut();
			$("#adminContainer").fadeIn();
	});

}

function startQuiz(userID, roomID){

	var buttonPre="<button type='button' style='width: 100%' class='btn btn-default' id='";
	var buttonMid="'>";
	var buttonPost="</button>";
	$.get(server+"/getQuizQuestion?idRoom="+roomID+"&idUser="+userID,function(data){
		console.log(data);
		var serverReply=JSON.parse(data);
		if (serverReply.error != null) {
			console.log("Error: " + serverReply.error);
			return;
		}

		var quizQuestionID=serverReply.id;
		var quizQuestionText=serverReply.question;
		var quizAnswers=serverReply.answers;
		$("#quizQuestionText").text(quizQuestionText);
		$.each(quizAnswers,function(i,value){
			$("#quizAnswerColumn").append(buttonPre+value.id+buttonMid+value.text+buttonPost)
			$("#"+value.id).click(function(){answerQuiz(quizQuestionID,value.id,userID,roomID)});
		});
	});


}

function answerQuiz(questionID,answerID,userID,roomID){
	$("#quizAnswerColumn").empty();
	$.get(server+"/postAnswer?quizQuestionId="+questionID+"&answerID="+answerID,function(data){
		serverRepply=JSON.parse(data);
		if (serverRepply.correct=="true"){
			alert("Correct answer");
		}
		else{
			alert("Incorrect answer\n the right answer was: "+serverRepply.correctAnswer.text);
		}
		startQuiz(userID,roomID);
	});
}