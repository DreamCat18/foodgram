                                    # TODO: Update Django Settings to Match Example

## Steps:
1. Update backend/constants.py: Add PAGE_SIZE = DEFAULT_PAGE_SIZE.
2. Update backend/users/models.py: Rename class CustomUser to User.
3. Update backend/users/auth_backend.py: Change CustomUser to User.
4. Update backend/users/admin.py: Change CustomUser to User.
5. Update backend/api/serializers.py: Rename CustomUserSerializer to UserGetSerializer, CustomUserCreateSerializer to UserPostSerializer.
6. Update backend/backend/settings.py: Replace with example code, adjusted for project (imports from backend.constants, paths, etc.).
7. Verify changes and run migrations if needed.

## Completed Tasks:
- [x] Edit backend/users/models.py: change class name to 'user'
- [x] Edit backend/users/admin.py: update register to 'user'
- [x] Edit backend/users/auth_backend.py: update references to 'user'
- [x] Edit backend/backend/settings.py: change AUTH_USER_MODEL to 'users.user'
- [x] Delete migration files in backend/users/migrations/ and backend/recipes/migrations/ (keep __init__.py)
- [x] Run python manage.py makemigrations
- [x] Run python manage.py migrate
- [x] Verify the migration completes without errors.
