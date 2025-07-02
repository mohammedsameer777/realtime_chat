from django.shortcuts import render

def room(request, room_name):
    name = request.GET.get("name", "")  # get name from ?name=User
    return render(request, "chat/room.html", {
        "room_name": room_name,
        "username": name
    })
