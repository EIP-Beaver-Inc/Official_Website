"""
Comprehensive backend API tests for BEAVER Marketing Site
Tests all endpoints: health, pipeline, defects, scoring, quiz, contact, demo-requests
"""
import requests
import sys
from typing import Dict, Any, List

# Public endpoint from frontend/.env
BASE_URL = "https://timber-vision-ai.preview.emergentagent.com/api"


class BeaverAPITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests: List[str] = []

    def test(self, name: str, method: str, endpoint: str, expected_status: int, 
             data: Dict = None, validate_fn=None) -> tuple[bool, Any]:
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code} (expected {expected_status})")
            
            if response.status_code != expected_status:
                print(f"   ❌ FAILED - Status mismatch")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, None

            # Parse JSON response
            try:
                json_data = response.json()
            except Exception as e:
                print(f"   ❌ FAILED - Invalid JSON: {e}")
                self.failed_tests.append(f"{name}: Invalid JSON response")
                return False, None

            # Run custom validation if provided
            if validate_fn:
                is_valid, error_msg = validate_fn(json_data)
                if not is_valid:
                    print(f"   ❌ FAILED - Validation: {error_msg}")
                    self.failed_tests.append(f"{name}: {error_msg}")
                    return False, json_data

            print(f"   ✅ PASSED")
            self.tests_passed += 1
            return True, json_data

        except requests.exceptions.Timeout:
            print(f"   ❌ FAILED - Request timeout")
            self.failed_tests.append(f"{name}: Timeout")
            return False, None
        except Exception as e:
            print(f"   ❌ FAILED - Exception: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, None

    def run_all_tests(self):
        """Execute all backend tests"""
        print("=" * 70)
        print("BEAVER BACKEND API TESTS")
        print("=" * 70)

        # ===== Health Check =====
        print("\n📋 HEALTH CHECK")
        self.test(
            "GET /api/health",
            "GET", "health", 200,
            validate_fn=lambda d: (
                (True, "") if d.get("status") == "healthy" and d.get("mongo") == "connected"
                else (False, f"Invalid health response: {d}")
            )
        )

        # ===== Pipeline Info =====
        print("\n📋 PIPELINE INFO")
        success, pipeline_data = self.test(
            "GET /api/pipeline",
            "GET", "pipeline", 200,
            validate_fn=lambda d: (
                (True, "") if (
                    "steps" in d and len(d["steps"]) == 3 and
                    "defect_classes" in d and len(d["defect_classes"]) == 9 and
                    "scoring_classes" in d and len(d["scoring_classes"]) == 4
                ) else (False, f"Invalid pipeline structure: steps={len(d.get('steps', []))}, defects={len(d.get('defect_classes', []))}, scoring={len(d.get('scoring_classes', []))}")
            )
        )

        # ===== Defects =====
        print("\n📋 DEFECTS")
        self.test(
            "GET /api/defects",
            "GET", "defects", 200,
            validate_fn=lambda d: (
                (True, "") if "defects" in d and len(d["defects"]) == 9
                else (False, f"Expected 9 defects, got {len(d.get('defects', []))}")
            )
        )

        # ===== Scoring =====
        print("\n📋 SCORING")
        self.test(
            "GET /api/scoring",
            "GET", "scoring", 200,
            validate_fn=lambda d: (
                (True, "") if "classes" in d and len(d["classes"]) == 4
                else (False, f"Expected 4 scoring classes, got {len(d.get('classes', []))}")
            )
        )

        # ===== Quiz Questions =====
        print("\n📋 QUIZ QUESTIONS")
        success, quiz_data = self.test(
            "GET /api/quiz/questions",
            "GET", "quiz/questions", 200,
            validate_fn=lambda d: (
                (True, "") if (
                    "product_types" in d and len(d["product_types"]) == 4 and
                    "quality_classes" in d and len(d["quality_classes"]) == 6 and
                    "questions" in d and len(d["questions"]) == 15 and
                    d.get("total") == 15 and
                    # Verify questions don't have correct_answer or explanation
                    all("correct_answer" not in q and "explanation" not in q for q in d["questions"])
                ) else (False, f"Invalid quiz structure: product_types={len(d.get('product_types', []))}, quality_classes={len(d.get('quality_classes', []))}, questions={len(d.get('questions', []))}, total={d.get('total')}")
            )
        )

        # ===== Quiz Submit - Empty Answers (should fail) =====
        print("\n📋 QUIZ SUBMIT - VALIDATION")
        self.test(
            "POST /api/quiz/submit with empty answers",
            "POST", "quiz/submit", 400,
            data={"answers": []}
        )

        # ===== Quiz Submit - All Correct Answers =====
        print("\n📋 QUIZ SUBMIT - ALL CORRECT")
        if success and quiz_data:
            # Build all correct answers (hardcoded from quiz_data.py)
            correct_answers = [
                {"question_id": "q1", "selected": "a"},
                {"question_id": "q2", "selected": "b"},
                {"question_id": "q3", "selected": "b"},
                {"question_id": "q4", "selected": "b"},
                {"question_id": "q5", "selected": "c"},
                {"question_id": "q6", "selected": "c"},
                {"question_id": "q7", "selected": "b"},
                {"question_id": "q8", "selected": "b"},
                {"question_id": "q9", "selected": "c"},
                {"question_id": "q10", "selected": "b"},
                {"question_id": "q11", "selected": "c"},
                {"question_id": "q12", "selected": "c"},
                {"question_id": "q13", "selected": "b"},
                {"question_id": "q14", "selected": "c"},
                {"question_id": "q15", "selected": "b"},
            ]
            
            self.test(
                "POST /api/quiz/submit with all correct answers (15/15)",
                "POST", "quiz/submit", 200,
                data={
                    "answers": correct_answers,
                    "email": "test@beaver.fr",
                    "nom": "Test User",
                    "entreprise": "Test Scierie"
                },
                validate_fn=lambda d: (
                    (True, "") if (
                        d.get("score") == 15 and
                        d.get("total") == 15 and
                        d.get("percentage") == 100.0 and
                        "details" in d and len(d["details"]) == 15 and
                        all(item.get("is_correct") for item in d["details"]) and
                        "id" in d and "completed_at" in d
                    ) else (False, f"Invalid quiz result: score={d.get('score')}, total={d.get('total')}, percentage={d.get('percentage')}, details_count={len(d.get('details', []))}")
                )
            )

        # ===== Quiz Submit - Mixed Answers =====
        print("\n📋 QUIZ SUBMIT - MIXED ANSWERS")
        if success and quiz_data:
            mixed_answers = [
                {"question_id": "q1", "selected": "a"},  # correct
                {"question_id": "q2", "selected": "a"},  # wrong
                {"question_id": "q3", "selected": "b"},  # correct
                {"question_id": "q4", "selected": "a"},  # wrong
                {"question_id": "q5", "selected": "c"},  # correct
                {"question_id": "q6", "selected": "a"},  # wrong
                {"question_id": "q7", "selected": "b"},  # correct
                {"question_id": "q8", "selected": "b"},  # correct
                {"question_id": "q9", "selected": "c"},  # correct
                {"question_id": "q10", "selected": "a"}, # wrong
                {"question_id": "q11", "selected": "c"}, # correct
                {"question_id": "q12", "selected": "c"}, # correct
                {"question_id": "q13", "selected": "b"}, # correct
                {"question_id": "q14", "selected": "c"}, # correct
                {"question_id": "q15", "selected": "b"}, # correct
            ]
            
            self.test(
                "POST /api/quiz/submit with mixed answers (11/15)",
                "POST", "quiz/submit", 200,
                data={"answers": mixed_answers},
                validate_fn=lambda d: (
                    (True, "") if (
                        d.get("score") == 11 and
                        d.get("total") == 15 and
                        abs(d.get("percentage", 0) - 73.3) < 0.1 and
                        "details" in d and len(d["details"]) == 15
                    ) else (False, f"Invalid quiz result: score={d.get('score')}, total={d.get('total')}, percentage={d.get('percentage')}")
                )
            )

        # ===== Quiz Results List =====
        print("\n📋 QUIZ RESULTS")
        self.test(
            "GET /api/quiz/results",
            "GET", "quiz/results", 200,
            validate_fn=lambda d: (
                (True, "") if isinstance(d, list)
                else (False, f"Expected list, got {type(d)}")
            )
        )

        # ===== Contact - Valid =====
        print("\n📋 CONTACT - VALID")
        self.test(
            "POST /api/contact with valid data",
            "POST", "contact", 200,
            data={
                "nom": "Jean Dupont",
                "entreprise": "Scierie du Morvan",
                "email": "jean.dupont@scierie-morvan.fr",
                "telephone": "+33 1 23 45 67 89",
                "message": "Je souhaite en savoir plus sur BEAVER pour notre scierie."
            },
            validate_fn=lambda d: (
                (True, "") if (
                    "id" in d and "created_at" in d and
                    d.get("nom") == "Jean Dupont" and
                    d.get("email") == "jean.dupont@scierie-morvan.fr"
                ) else (False, f"Invalid contact response: {d}")
            )
        )

        # ===== Contact - Invalid Email =====
        print("\n📋 CONTACT - VALIDATION")
        self.test(
            "POST /api/contact with invalid email",
            "POST", "contact", 422,
            data={
                "nom": "Test",
                "email": "invalid-email",
                "message": "Test message"
            }
        )

        # ===== Contact - Missing Message =====
        self.test(
            "POST /api/contact without message",
            "POST", "contact", 422,
            data={
                "nom": "Test",
                "email": "test@example.com"
            }
        )

        # ===== Contact List =====
        print("\n📋 CONTACT LIST")
        self.test(
            "GET /api/contact",
            "GET", "contact", 200,
            validate_fn=lambda d: (
                (True, "") if isinstance(d, list)
                else (False, f"Expected list, got {type(d)}")
            )
        )

        # ===== Demo Request - Valid =====
        print("\n📋 DEMO REQUEST - VALID")
        self.test(
            "POST /api/demo-requests with valid data",
            "POST", "demo-requests", 200,
            data={
                "nom": "Marie Martin",
                "entreprise": "Scierie des Vosges",
                "email": "marie.martin@vosges-bois.fr",
                "telephone": "+33 3 29 12 34 56",
                "taille_scierie": "50-100 employés",
                "volume": "10000 m³/an",
                "message": "Nous aimerions une démonstration de BEAVER."
            },
            validate_fn=lambda d: (
                (True, "") if (
                    "id" in d and "created_at" in d and
                    d.get("nom") == "Marie Martin" and
                    d.get("entreprise") == "Scierie des Vosges"
                ) else (False, f"Invalid demo request response: {d}")
            )
        )

        # ===== Demo Request - Missing Required Fields =====
        print("\n📋 DEMO REQUEST - VALIDATION")
        self.test(
            "POST /api/demo-requests without required fields",
            "POST", "demo-requests", 422,
            data={
                "nom": "Test"
                # missing entreprise and email
            }
        )

        # ===== Demo Request List =====
        print("\n📋 DEMO REQUEST LIST")
        self.test(
            "GET /api/demo-requests",
            "GET", "demo-requests", 200,
            validate_fn=lambda d: (
                (True, "") if isinstance(d, list)
                else (False, f"Expected list, got {type(d)}")
            )
        )

        # ===== Print Summary =====
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {len(self.failed_tests)} ❌")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, failure in enumerate(self.failed_tests, 1):
                print(f"  {i}. {failure}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")
        print("=" * 70)

        return 0 if len(self.failed_tests) == 0 else 1


def main():
    tester = BeaverAPITester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
