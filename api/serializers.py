from .models import Task, Category, UserProfile
from rest_framework import serializers
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
	
	password = serializers.CharField(write_only=True)
	
	class Meta:
		model = User
		fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
		
	def create(self, validated_data):
		user = User.objects.create_user(
			username = validated_data['username'], 
			first_name=validated_data['first_name'],
		    last_name=validated_data['last_name'], 
		    email=validated_data['email'], 
		    password=validated_data['password']
		   )
		return user



class LoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField()
	

class TaskSerializer(serializers.ModelSerializer):
  user = serializers.ReadOnlyField(source='user.username')
  assigned_to = serializers.ReadOnlyField(source='user.username')
  category= serializers.StringRelatedField(source='category.name', read_only=True)
  date_created = serializers.SerializerMethodField()
  
  class Meta:
    model = Task
    fields = '__all__'
  
  def create(self, validated_data):
    validated_data['user'] = self.context['request'].user
    return super().create(validated_data)
  
  def get_date_created(self, obj):
    return obj.date_created.strftime('%b %d, %Y')
    
class CategorySerializer(serializers.ModelSerializer):
  user = serializers.ReadOnlyField(source='user.username')
  
  class Meta:
    model = Category
    fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = UserProfile
		fields = ['bio', 'profile_picture']

class UserProfileDetailSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    assigned_to = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserProfile
        fields = '__all__'