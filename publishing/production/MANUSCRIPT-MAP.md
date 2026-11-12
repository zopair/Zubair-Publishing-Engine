# Bilingual Manuscript Map
## A Gift from the One Who Left / هدية من الغائب

**Canonical count:** 36 chapters + epilogue in each language.

This map is a production/navigation reference. It does not authorize rewriting, renaming story events, or changing chapter content.

## Narrative architecture

### Part I — The relationship and the wedding that never happens
**Chapters 1–30**

The first part follows Emily Bennett and Michael Reed from their early connection and shared years through friendship, family life, growing love, engagement, and preparations for their wedding.

The emotional destination of Part I is the wedding day. Michael leaves for the wedding venue and dies in a road accident before arriving. The wedding never takes place.

### Part II — Grief, memory, and what remains
**Chapters 31–36 + Epilogue**

The second part follows the immediate aftermath, the funeral, the families' grief, Emily's gradual return to life, the preservation of Michael's authentic photographs/messages/recordings, and the ethical questions surrounding the EverAfter project.

**Continuity lock:** No chapter after Chapter 30 may imply that Michael and Emily married, began married life, or went on a honeymoon. The old English honeymoon and married-life drafts are archived and excluded from every release build.

## English chapter sequence

| No. | Canonical chapter title |
|---:|---|
| 1 | The Seat by the Window |
| 2 | The Art of Being Late |
| 3 | An Unexpected Invitation |
| 4 | The Things We Inherit |
| 5 | A Table for Four |
| 6 | The Exhibition of Small Things |
| 7 | The Space Between Words |
| 8 | The Evening Everyone Came |
| 9 | A Small Kind of Courage |
| 10 | The Weather of Us |
| 11 | The Colour of a Room |
| 12 | The Map of Next Summer |
| 13 | The Long Way Home |
| 14 | The Room Full of Voices |
| 15 | The Presentation Day |
| 16 | A Season of Small Goodbyes |
| 17 | The Things We Carry Forward |
| 18 | The First Real Choice |
| 19 | Two Campuses, One Sky |
| 20 | The Language of New Friends |
| 21 | The Promise in the Details |
| 22 | The Shape of a Future |
| 23 | What the Heart Remembers |
| 24 | The Question Before the Question |
| 25 | The Day of the Question |
| 26 | The Women Who Made a Wedding |
| 27 | The House of Small Decisions |
| 28 | The Dress and the Vows |
| 29 | The Night Before Morning |
| 30 | The Day We Chose |
| 31 | The Morning That Never Came |
| 32 | The Things That Remain |
| 33 | A Gift Without a Reason |
| 34 | The Questions We Must Ask |
| 35 | The Price of a Voice |
| 36 | A Place to Remember |

**Epilogue:** Some Memories Refuse to Say Goodbye

## Arabic chapter sequence

| رقم | عنوان الفصل المعتمد في المخطوطة |
|---:|---|
| 1 | المقعد المجاور للنافذة |
| 2 | فن التأخر عن المواعيد |
| 3 | دعوة غير متوقعة |
| 4 | ما نورثه من الآخرين |
| 5 | مائدة لأربعة أشخاص |
| 6 | معرض الأشياء الصغيرة |
| 7 | المسافة بين الكلمات |
| 8 | الأمسية التي حضر فيها الجميع |
| 9 | شجاعة صغيرة |
| 10 | طقسنا الخاص |
| 11 | لون الغرفة |
| 12 | خريطة الصيف القادم |
| 13 | الطريق الطويل إلى البيت |
| 14 | الغرفة الممتلئة بالأصوات |
| 15 | يوم العرض |
| 16 | موسم من الوداعات الصغيرة |
| 17 | ما نحمله معنا إلى الأمام |
| 18 | الاختيار الحقيقي الأول |
| 19 | حرمان جامعيان وسماء واحدة |
| 20 | لغة الأصدقاء الجدد |
| 21 | الوعد الكامن في التفاصيل |
| 22 | ملامح المستقبل |
| 23 | ما يتذكره القلب |
| 24 | السؤال الذي يسبق السؤال |
| 25 | يوم السؤال |
| 26 | النساء اللواتي صنعن حفل الزفاف |
| 27 | بيت القرارات الصغيرة |
| 28 | الفستان والعهود |
| 29 | الليلة التي تسبق الصباح |
| 30 | اليوم الذي اخترناه |
| 31 | الصباح الذي لم يأتِ |
| 32 | الأشياء التي تبقى |
| 33 | هدية بلا مناسبة |
| 34 | الأسئلة التي يجب أن نطرحها |
| 35 | ثمن الصوت |
| 36 | مكان للتذكر |

**الخاتمة:** بعض الذكريات ترفض الوداع

## Assembly and source-file rules

- Use the consolidated master in each language as the formatting assembly source.
- Retain the individual chapter files for controlled editing and traceability.
- English Chapters 14 and 15 are stored one level deeper in their own folders; the assembly process must include their Markdown files and must not mistake those folders for missing chapters.
- The Arabic chapter index is in `manuscript/ar/README.md`.
- Do not assemble from `manuscript/archive/`.
- Preserve chapter order, titles, paragraph order, dialogue, and the epilogue.
- Before export, verify exactly 36 numbered chapter headings and one epilogue heading in each master.