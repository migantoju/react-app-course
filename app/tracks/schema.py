import graphene
from graphene_django import DjangoObjectType
from .models import Track, Like
from users.schema import UserType
from graphql import GraphQLError
from django.db.models import Q

class TrackType(DjangoObjectType):

    class Meta:
        model = Track

class LikeType(DjangoObjectType):

    class Meta:
        model = Like

class Query(graphene.ObjectType):

    tracks = graphene.List(TrackType, search=graphene.String())
    track = graphene.Field(TrackType, id=graphene.Int(required=True))
    likes = graphene.List(LikeType)

    def resolve_tracks(self, info, search=None):
        if search:
            filter = (
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(url__icontains=search) |
                Q(posted_by__username__icontains=search)
            )
            return Track.objects.filter(filter)
        return Track.objects.all()

    def resolve_track(self, info, id):
        return Track.objects.get(id=id)

    def resolve_likes(self, info):
        return Like.objects.all()

class CreateTrack(graphene.Mutation):

    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, title, description, url):

        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Log in to add a track')

        track = Track(title=title, description=description, url=url, posted_by=user)
        track.save()
        return CreateTrack(track=track)

class UpdateTrack(graphene.Mutation):
    
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, track_id, title, url, description):
        user = info.context.user
        track = Track.objects.get(id=track_id)

        if track.posted_by != user:
            raise GraphQLError("No tiene permisos para actualizar")
        
        track.title = title
        track.description = description
        track.url = url

        track.save()

        return UpdateTrack(track=track)

class DeleteTrack(graphene.Mutation):

    track_id = graphene.Int()

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        track = Track.objects.get(id=track_id)

        if track.posted_by != user:
            raise GraphQLError("No tienes permisos para eliminar éste Track.")

        track.delete()

        return DeleteTrack(track_id=track_id)

class CreateLike(graphene.Mutation):

    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Debes iniciar sesión primero.')

        track = Track.objects.get(id=track_id)

        if not track:
            raise GraphQLError("No existe un track con el ID proporcionado.")

        userLike = Like.objects.filter(user=user, track=track)

        if userLike.exists():
            userLike.delete() 
        else:
            Like.objects.create(
                user=user,
                track=track
            )
            print("Has dado like a {}".format(track_id))

        return CreateLike(user=user, track=track)


class Mutation(graphene.ObjectType):

    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    
    create_like = CreateLike.Field()