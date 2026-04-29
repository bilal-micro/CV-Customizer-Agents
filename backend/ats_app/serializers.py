from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from ats_app.models import Job, ProcessRun, StageResult, UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and profile"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Create profile for new user with empty fields
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (OpenRouter API key and preferred model)"""
    class Meta:
        model = UserProfile
        fields = ['id', 'openrouter_api_key', 'preferred_model']
        extra_kwargs = {
            'openrouter_api_key': {
                'write_only': True,  # Don't expose API key in responses
                'required': False,
                'allow_blank': True
            },
            'preferred_model': {
                'required': False,
                'allow_blank': True
            }
        }
    
    def validate_openrouter_api_key(self, value):
        """Validate OpenRouter API key format if provided"""
        if value and value.strip():
            # Basic format validation - OpenRouter keys typically start with 'sk-or-'
            if not value.strip().startswith('sk-or-'):
                raise serializers.ValidationError(
                    "Invalid OpenRouter API key format. API keys should start with 'sk-or-'. "
                    "Get your API key from https://openrouter.ai/keys"
                )
            return value.strip()
        return ''
    
    def validate_preferred_model(self, value):
        """Validate preferred model if provided"""
        if value and value.strip():
            return value.strip()
        return ''


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value



class StageResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageResult
        fields = ['id', 'stage', 'status', 'result', 'rating', 'notes', 'iteration_notes', 'manual_feedback', 'iteration_number', 'created_at', 'updated_at']


class ProcessRunSerializer(serializers.ModelSerializer):
    stage_results = StageResultSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProcessRun
        fields = ['id', 'job', 'status', 'retry_count', 'max_retries', 'iteration_count', 'max_iterations', 'manual_latex_input', 'original_latex', 'stage_results', 'user', 'username', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class JobSerializer(serializers.ModelSerializer):
    process_runs = ProcessRunSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'latex_cv', 'process_runs', 'user', 'username', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id' , 'title', 'description', 'latex_cv']

    def create(self, validated_data):
        # Set the current user when creating a job
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProcessRunCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessRun
        fields = ['job', 'max_retries']

    def create(self, validated_data):
        # Set the user from the job
        job = validated_data['job']
        validated_data['user'] = job.user
        return super().create(validated_data)


class ManualLatexSubmissionSerializer(serializers.Serializer):
    latex_content = serializers.CharField(required=True)

    def validate_latex_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("LaTeX content cannot be empty")
        
        # Basic LaTeX validation
        if r'\begin{document}' not in value:
            raise serializers.ValidationError("LaTeX must contain \\begin{document}")
        
        if r'\end{document}' not in value:
            raise serializers.ValidationError("LaTeX must contain \\end{document}")
        
        return value
