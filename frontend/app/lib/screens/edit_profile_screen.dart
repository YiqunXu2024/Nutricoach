import 'package:flutter/material.dart';
import '../services/api_service.dart';

class EditProfileScreen extends StatefulWidget {
  final Map<String, dynamic>? profile;
  EditProfileScreen({this.profile});

  @override
  _EditProfileScreenState createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  double? height, weight, targetWeight;
  bool isVegetarian = false;
  String? allergies, chronicDiseases, gender;
  int? age;

  @override
  void initState() {
    super.initState();
    final p = widget.profile ?? {};
    height = p['height']?.toDouble();
    weight = p['weight']?.toDouble();
    targetWeight = p['target_weight']?.toDouble();
    isVegetarian = p['is_vegetarian'] ?? false;
    allergies = p['allergies'];
    chronicDiseases = p['chronic_diseases'];
    age = p['age'];
    gender = p['gender'];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Edit Profile'), backgroundColor: Colors.green),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              _buildNumberField('Height (cm)', height, (v) => height = v),
              _buildNumberField('Weight (kg)', weight, (v) => weight = v),
              _buildNumberField('Target Weight (kg)', targetWeight, (v) => targetWeight = v),
              SwitchListTile(
                title: Text('Vegetarian'),
                value: isVegetarian,
                onChanged: (v) => setState(() => isVegetarian = v),
              ),
              _buildTextField('Allergies (comma separated)', allergies, (v) => allergies = v),
              _buildTextField('Chronic Diseases (comma separated)', chronicDiseases, (v) => chronicDiseases = v),
              _buildNumberField('Age', age?.toDouble(), (v) => age = v?.toInt()),
              DropdownButtonFormField<String>(
                value: gender,
                items: ['male', 'female', 'other'].map((g) => DropdownMenuItem(value: g, child: Text(g))).toList(),
                onChanged: (v) => setState(() => gender = v),
                decoration: InputDecoration(labelText: 'Gender'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                child: Text('Save'),
                onPressed: () async {
                  if (_formKey.currentState!.validate()) {
                    final data = {
                      'height': height,
                      'weight': weight,
                      'target_weight': targetWeight,
                      'is_vegetarian': isVegetarian,
                      'allergies': allergies,
                      'chronic_diseases': chronicDiseases,
                      'age': age,
                      'gender': gender,
                    };
                    await updateProfile(data); 
                    Navigator.pop(context, true);
                  }
                },
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNumberField(String label, double? initial, Function(double?) onSaved) {
    return TextFormField(
      initialValue: initial?.toString(),
      decoration: InputDecoration(labelText: label),
      keyboardType: TextInputType.number,
      onChanged: (v) => onSaved(double.tryParse(v)),
    );
  }

  Widget _buildTextField(String label, String? initial, Function(String) onSaved) {
    return TextFormField(
      initialValue: initial,
      decoration: InputDecoration(labelText: label),
      onChanged: onSaved,
    );
  }
}
