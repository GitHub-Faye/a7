# 任务14.1 实现计划：创建Exercise和StudentAnswer模型的序列化器

## 任务概述
开发序列化器来处理Exercise（练习题）和StudentAnswer（学生答案）模型的数据验证和转换，确保序列化器支持这些模型的所有字段，并提供必要的验证逻辑。

## 序列化器实现方案

### 1. Exercise模型序列化器

#### 1.1 ExerciseSerializer（读取操作）
- 包含所有Exercise模型字段
- 添加额外字段：
  - `knowledge_point_title`: 显示关联知识点标题
  - `type_display`: 显示题目类型的中文名称
  - `difficulty_display`: 显示难度等级的中文名称
- 所有字段设为只读

#### 1.2 ExerciseCreateSerializer（创建操作）
- 包含可写字段：title, content, type, difficulty, knowledge_point, answer_template
- 验证逻辑：
  - 使用ValidationUtils.validate_text_field验证title和content
  - 验证type是否为有效的题目类型
  - 验证difficulty是否在1-5范围内
  - 验证knowledge_point是否存在

#### 1.3 ExerciseUpdateSerializer（更新操作）
- 类似ExerciseCreateSerializer，但不包括knowledge_point字段
- 添加验证逻辑，确保标题在同一知识点下唯一（排除自身）

### 2. StudentAnswer模型序列化器

#### 2.1 StudentAnswerSerializer（读取操作）
- 包含所有StudentAnswer模型字段
- 添加额外字段：
  - `student_name`: 显示学生姓名
  - `exercise_title`: 显示练习题标题
- 所有字段设为只读

#### 2.2 StudentAnswerCreateSerializer（创建操作）
- 包含可写字段：exercise, content
- student字段自动设置为当前请求用户
- 验证逻辑：
  - 使用ValidationUtils.validate_text_field验证content
  - 验证exercise是否存在
  - 验证用户是否已经回答过该练习题（利用unique_together约束）

#### 2.3 StudentAnswerUpdateSerializer（更新操作）
- 仅包含content字段（学生只能更新自己的答案内容）
- 使用ValidationUtils.validate_text_field验证content

### 3. StudentAnswerFeedbackSerializer（教师反馈操作）
- 包含可写字段：score, feedback
- 只有教师和管理员可以使用
- 验证逻辑：
  - 验证score是否在合理范围内（可根据exercise类型决定）
  - 使用ValidationUtils.validate_text_field验证feedback

## 实现步骤

1. 在`a7/courses/serializers.py`中创建以上序列化器类
2. 为每个序列化器实现所需的验证方法
3. 利用现有的ValidationUtils工具类进行字段验证
4. 添加额外的验证逻辑，确保数据一致性
5. 对于创建操作，添加适当的逻辑自动设置某些字段（如StudentAnswerCreateSerializer中的student字段）
6. 编写单元测试，验证序列化器的功能和验证逻辑

## 注意事项

1. 权限控制将在后续任务中实现，但序列化器设计应考虑不同用户角色的操作权限
2. 需确保序列化器返回的数据格式与现有API一致
3. 验证逻辑应严格检查所有输入数据，防止无效数据进入系统
4. 序列化器应支持嵌套关系，以便前端可以获取完整的关联数据

## 技术参考
- 遵循项目已有序列化器的实现模式（如CourseSerializer、CoursewareSerializer等）
- 利用ValidationUtils类进行统一的字段验证
- 使用Django REST Framework的ModelSerializer功能
- 使用SerializerMethodField添加自定义字段
