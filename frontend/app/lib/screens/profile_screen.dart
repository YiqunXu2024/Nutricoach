import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'edit_profile_screen.dart';

class ProfileScreen extends StatefulWidget {
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String? username;
  String? email;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
    final user = await fetchUserMe();
    setState(() {
      username = user?['username'] ?? '';
      email = user?['email'] ?? '';
    });
  }

  void _showChangePasswordDialog() {
    final oldPwdController = TextEditingController();
    final newPwdController = TextEditingController();
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Change Password'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: oldPwdController,
                obscureText: true,
                decoration: InputDecoration(labelText: 'Old Password'),
              ),
              TextField(
                controller: newPwdController,
                obscureText: true,
                decoration: InputDecoration(labelText: 'New Password'),
              ),
            ],
          ),
          actions: [
            TextButton(
              child: Text('Cancel'),
              onPressed: () => Navigator.pop(context),
            ),
            ElevatedButton(
              child: Text('Confirm'),
              onPressed: () async {
                final oldPwd = oldPwdController.text;
                final newPwd = newPwdController.text;
                try {
                  await changePassword(oldPwd, newPwd);
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Password changed successfully')));
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to change password')));
                }
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            ),
          ],
        );
      },
    );
  }

  void _showFeedbackDialog() {
    String type = 'Function Issue';
    String desc = '';
    String contact = '';
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Help & Feedback'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('This is a demo feature for academic purposes.'),
                SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: type,
                  items: ['Function Issue', 'Suggestion', 'Other'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                  onChanged: (v) => type = v ?? 'Function Issue',
                  decoration: InputDecoration(labelText: 'Issue Type'),
                ),
                TextFormField(
                  maxLines: 3,
                  decoration: InputDecoration(labelText: 'Issue Description'),
                  onChanged: (v) => desc = v,
                ),
                TextFormField(
                  decoration: InputDecoration(labelText: 'Optional Email (we won\'t reply, but you can leave your information)'),
                  onChanged: (v) => contact = v,
                ),
                SizedBox(height: 10),
                Text('Note:', style: TextStyle(fontWeight: FontWeight.bold)),
                Text('This is a demo feature for academic purposes.\nIn the real app, feedback would help us improve the app based on user needs.', style: TextStyle(fontSize: 12, color: Colors.grey)),
                SizedBox(height: 20),
                Text('FAQ', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 5),
                Text('Q: Is this app free to use?\nA: Yes, NutriCoach is a free app developed for academic research purposes only.\n'),
                Text('Q: Is the nutritional advice medically certified?\nA: No, the app provides AI-generated suggestions based on public UK guidelines. Please consult a healthcare professional for personalized advice.\n'),
                Text('Q: Will my data be stored or shared?\nA: All data is stored locally for testing and academic evaluation only, and is not shared.'),
              ],
            ),
          ),
          actions: [
            TextButton(
              child: Text('Close'),
              onPressed: () => Navigator.pop(context),
            ),
          ],
        );
      },
    );
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('About Us'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('About NutriCoach', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 5),
                Text('NutriCoach is a student-led project developed as part of a master\'s dissertation at the University of Glasgow.'),
                SizedBox(height: 5),
                Text('The app aims to help individuals improve their dietary habits through AI-driven analysis and personalized nutritional advice, based on UK guidelines such as the NHS Eatwell Guide.'),
                SizedBox(height: 5),
                Text('Users can log meals in natural language and receive instant feedback, making healthy eating easier and more accessible.'),
                SizedBox(height: 5),
                Text('This project is academic and not intended for commercial or medical use.'),
                SizedBox(height: 10),
                Text('Development Period: June 2025 – August 2025'),
                //Text('Supervisor: Dr. John Smith'),
                Text('Technology Stack: Flutter, FastAPI, ollama+llama, PostgreSQL'),
              ],
            ),
          ),
          actions: [
            TextButton(
              child: Text('Close'),
              onPressed: () => Navigator.pop(context),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Profile'),
        backgroundColor: Colors.green,
      ),
      body: ListView(
        padding: EdgeInsets.all(16.0),
        children: [
          // user info card
          Card(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.green,
                    child: Icon(
                      Icons.person,
                      size: 50,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(height: 15),
                  Text(
                    username ?? '',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    email ?? '',
                    style: TextStyle(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          // settings
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: Icon(Icons.edit, color: Colors.blue),
                  title: Text('Edit Profile'),
                  trailing: Icon(Icons.arrow_forward_ios),
                  onTap: () async {
                    final profile = await fetchProfile();
                    final updated = await Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => EditProfileScreen(profile: profile)),
                    );
                    if (updated == true) {
                      setState(() {});
                    }
                  },
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.lock, color: Colors.orange),
                  title: Text('Change Password'),
                  trailing: Icon(Icons.arrow_forward_ios),
                  onTap: _showChangePasswordDialog,
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.help, color: Colors.grey),
                  title: Text('Help & Feedback'),
                  trailing: Icon(Icons.arrow_forward_ios),
                  onTap: _showFeedbackDialog,
                ),
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.info, color: Colors.grey),
                  title: Text('About Us'),
                  trailing: Icon(Icons.arrow_forward_ios),
                  onTap: _showAboutDialog,
                ),
              ],
            ),
          ),
          SizedBox(height: 20),
          // logout button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              child: Text(
                'Logout',
                style: TextStyle(fontSize: 16),
              ),
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (BuildContext context) {
                    return AlertDialog(
                      title: Text('Confirm Logout'),
                      content: Text('Are you sure you want to logout?'),
                      actions: [
                        TextButton(
                          child: Text('Cancel'),
                          onPressed: () {
                            Navigator.of(context).pop();
                          },
                        ),
                        ElevatedButton(
                          child: Text('Confirm'),
                          onPressed: () {
                            // TODO: clear login status
                            Navigator.of(context).pop();
                            Navigator.pushReplacementNamed(context, '/login');
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    );
                  },
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(vertical: 15),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 