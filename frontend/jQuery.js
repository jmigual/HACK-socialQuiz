function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}


var server = "http://localhost:5000";
var server2 = "http:interact.siliconpeople.net"

urlVars=getUrlVars();
if ("id" in urlVars){
	var roomID = urlVars["id"];
	$.get(server+"/statusRoom?id="+roomID,function(data){
		serverRepply=JSON.parse(data);
		if (serverRepply.status != "started" && serverRepply.status!= "waiting"){
			$("#emailContainer").fadeOut();
			$("#errorContainer").fadeIn();
		}
	});
}

$(document).ready(function(){
	$("#emailInput").focus();
	$(document).keypress(function(e){
		if (e.which == 13){
			var email = $("#emailInput").val();
			$.get(server + "/getUserId?email="+email,function(data){

				serverRepply=JSON.parse(data);
				var userID = serverRepply.id;
				endEmail(userID,email);
				$(document).off("keypress");
			});
		}
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

function startAdmin(userID){
	$("#adminContainer").fadeIn();
	$("#newRoom").click(function(){newRoom(userID)});
	$("#checkboxContainer").empty();

	var part1="<p style=\"display: inline; color: white\">Room #<b>";//ID
	var part2="</b> status: ";//status
	var part3="</p>"
	var part35="\n<button type=\"button\" class=\"btn btn-default\" id=\"";//ID
	var part4="\">";//buttonText
	var part5="</button><br>";

	$.get(server+"/getRooms?userId="+userID,function(data){
		serverRepply=JSON.parse(data);
		var rooms= serverRepply.rooms;
		for (var i=0; i<rooms.length; i++){
			var r=rooms[i];

			$.get(server+"/statusRoom?id="+r,function(data){
				serverRepply=JSON.parse(data);
				var status=serverRepply.status;
				if (status=="waiting"){
					next="started";
					$("#checkboxContainer").append(part1+r+part2+status+part3+part35+r+part4+"START");
					$("#"+r).click(function(){
						$.get(server+"/openRoom?id="+r,function(){
							startAdmin(userID);
						});
					})
				}
				else if (status=="started"){
					next="finished";
					$("#checkboxContainer").append(part1+r+part2+status+part3+part35+r+part4+"FINISH");
					$("#"+r).click(function(){
						$.get(server+"/finishRoom?id="+r,function(){
							startAdmin(userID);
						});
					})
				}
				else if (status=="finished"){
					$("#checkboxContainer").append(part1+r+part2+status+part3);
				}
				/*var open='off';
				if (serverRepply.status == "started") open='on';
				$("#"+r).bootstrapToggle({
					on: 'Open',
					off: 'Closed'
				}).bootstrapToggle(open).change(function(){
					if($(this).prop('checked')){
						$.get(server+"/openRoom?id="+r,function(data){});
					}
					else{
						$.get(server+"/closeRoom?id="+r,function(data){});
					}
				});*/
			});
		}
	});
}

function newRoom(userID){
	$("#adminContainer").fadeOut();
	$("#newRoomContainer").fadeIn();
	newQuestions=[];
	$(document).keypress(function(e){
		if (e.which==13){
			newQuestions.push($("#questionInput").val());
			$("#questionInput").val("");	
		}
	});
	$("#finishRoom").click(function(){
		$.get(server+"/createRoom?userId="+userID,function(data){
			serverRepply=JSON.parse(data);
			roomID=serverRepply.id;
			$.ajax({
	            url:server+"/fillRoom",
	            data:JSON.stringify({
	            	id:roomID,
					question:newQuestions
				}),
				contentType:"application/json; charset=utf-8",
				type:"POST"
			});
			$("#questionInput").val("");
			$(document).off("keypress");
			$("#finishRoom").off("click");
			$("#cancelRoom").off("click");
			$("#newRoomContainer").fadeOut();
			$("#adminContainer").fadeIn();
			alert(roomID);
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

	var buttonPre="<button type=\"button\" style=\"width: 100%\" class=\"btn btn-default\" id=\"";
	var buttonMid="\">";
	var buttonPost="</button>";
	$.get(server+"/getQuizQuestion?idRoom="+roomID+"&idUser="+userID,function(data){
	console.log(data);
		serverRepply=JSON.parse(data);
		quizQuestionID=serverRepply.id;
		quizQuestionText=serverRepply.question;
		quizAnswers=serverRepply.answers;
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