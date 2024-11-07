package com.example.descipher

import android.app.Activity
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.spec.SecretKeySpec
import android.util.Base64
import javax.crypto.spec.IvParameterSpec
import java.net.URLEncoder
import java.net.URLDecoder

@OptIn(ExperimentalMaterial3Api::class)
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val navController = rememberNavController()
            Surface {
                NavHost(navController = navController, startDestination = "main") {
                    composable("main") { MainScreen(navController) }
                    composable("create_file") { CreateFileScreen(navController) }
                    composable(
                        "parameters/{text}",
                        arguments = listOf(navArgument("text") { type = NavType.StringType })
                    ) { backStackEntry ->
                        val text = backStackEntry.arguments?.getString("text") ?: ""
                        ParametersScreen(navController, text)
                    }
                    composable(
                        "result_screen/{resultText}",
                        arguments = listOf(navArgument("resultText") { type = NavType.StringType })
                    ) { backStackEntry ->
                        val resultText = backStackEntry.arguments?.getString("resultText") ?: ""
                        ResultScreen(resultText)
                    }
                }
            }
        }
    }
}

@Composable
fun MainScreen(navController: NavController) {
    val activity = LocalContext.current as? Activity
    val showDialog = remember { mutableStateOf(false) }

    val openFileLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            val contentResolver = activity?.contentResolver
            val inputStream = contentResolver?.openInputStream(it)
            val fileContent = inputStream?.bufferedReader().use { reader -> reader?.readText() }

            navController.navigate("parameters/${fileContent}")
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(
            onClick = { navController.navigate("create_file") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = "Створити файл")
        }

        Button(
            onClick = { openFileLauncher.launch("text/plain") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = "Відкрити файл")
        }

        Button(
            onClick = { showDialog.value = true },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = "Відомості про розробника")
        }

        Button(
            onClick = { activity?.finish() },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = "Вихід із системи")
        }

        if (showDialog.value) {
            DeveloperInfoDialog(onDismiss = { showDialog.value = false })
        }
    }
}

@Composable
fun CreateFileScreen(navController: NavController) {
    val textInput = remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        TextField(
            value = textInput.value,
            onValueChange = { textInput.value = it },
            label = { Text("Введіть текст") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = {
                navController.navigate("parameters/${textInput.value}")
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Text("Далі")
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParametersScreen(navController: NavController, text: String) {
    val selectedMode = remember { mutableStateOf("ECB") }
    val keyExpanded = remember { mutableStateOf(false) }

    val cipher = DESCrypto(mode = selectedMode.value)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        ExposedDropdownMenuBox(
            expanded = keyExpanded.value,
            onExpandedChange = { keyExpanded.value = !keyExpanded.value }
        ) {
            TextField(
                modifier = Modifier.menuAnchor(),
                value = selectedMode.value,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = keyExpanded.value) }
            )

            ExposedDropdownMenu(
                expanded = keyExpanded.value,
                onDismissRequest = { keyExpanded.value = false },
                modifier = Modifier.width(200.dp)
            ) {
                listOf("ECB", "CBC", "CFB", "OFB").forEach { key ->
                    DropdownMenuItem(
                        text = { Text(text = key) },
                        onClick = {
                            selectedMode.value = key
                            keyExpanded.value = false
                        },
                        contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding
                    )
                }
            }
        }

        Button(
            onClick = {
                val encryptedText = URLEncoder.encode(cipher.encrypt(text), "UTF-8")
                navController.navigate("result_screen/$encryptedText")
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Text("Шифрувати")
        }

        Button(
            onClick = {
                val decryptedText = URLDecoder.decode(cipher.decrypt(text), "UTF-8")
                navController.navigate("result_screen/$decryptedText")
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Text("Розшифрувати")
        }
    }
}

class DESCrypto(private var mode: String) {

    private val algorithm = "DES"
    private val secretKey: SecretKey = SecretKeySpec("12345678".toByteArray(), algorithm)

    private val iv = IvParameterSpec(ByteArray(8) { 0x00 })

    private val transformation: String
        get() = "$algorithm/$mode/PKCS5Padding"

    fun encrypt(plainText: String): String {
        val cipher = Cipher.getInstance(transformation)
        if (mode == "ECB") {
            cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        } else {
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, iv)
        }
        val encryptedBytes = cipher.doFinal(plainText.toByteArray())
        return Base64.encodeToString(encryptedBytes, Base64.DEFAULT)
    }

    fun decrypt(encryptedText: String): String {
        val cipher = Cipher.getInstance(transformation)
        if (mode == "ECB") {
            cipher.init(Cipher.DECRYPT_MODE, secretKey)
        } else {
            cipher.init(Cipher.DECRYPT_MODE, secretKey, iv)
        }
        val decodedBytes = Base64.decode(encryptedText, Base64.DEFAULT)
        val decryptedBytes = cipher.doFinal(decodedBytes)
        return String(decryptedBytes)
    }
}

@Composable
fun ResultScreen(resultText: String) {
    val context = LocalContext.current

    val saveFileLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.CreateDocument("text/plain")
    ) { uri ->
        uri?.let {
            val outputStream = context.contentResolver.openOutputStream(it)
            outputStream?.use { stream ->
                stream.write(resultText.toByteArray())
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = resultText,
            modifier = Modifier.padding(16.dp),
            style = MaterialTheme.typography.bodyLarge
        )

        Button(
            onClick = {
                saveFileLauncher.launch("result.txt")
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Зберегти в .txt")
        }

        Button(
            onClick = { /* TODO: Додати логіку для друку файлів */ },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text("Роздрукувати")
        }
    }
}

@Composable
fun DeveloperInfoDialog(onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(text = "Відомості про розробника")
        },
        text = {
            Text(text = "Розробник: Піховкіна Катерина\nГрупа: ТВ-12")
        },
        confirmButton = {
            Button(
                onClick = onDismiss
            ) {
                Text("ОК")
            }
        }
    )
}