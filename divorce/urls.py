'''
Этот файл — часть divorce_project.

divorce_project -- веб-сервис по моделированию имущественных последствий для лица
на случай вступления в брак и развода по законодательству Российской Федерации
Copyright © 2020 Evgenii Kovalenko <kovalenko_evgeny@bk.ru>

divorce_project - свободная программа: вы можете перераспространять ее и/или
изменять ее на условиях Афферо Стандартной общественной лицензии GNU в том виде,
в каком она была опубликована Фондом свободного программного обеспечения;
либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
версии.

divorce_project распространяется в надежде, что она будет полезной,
но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Афферо Стандартной
общественной лицензии GNU.

Вы должны были получить копию Афферо Стандартной общественной лицензии GNU
вместе с этой программой. Если это не так, см.
<https://www.gnu.org/licenses/>.)
'''

from django.urls import path
from .views import *
urlpatterns = [
    path('', DivorceView.as_view(), name='main'),
    path('del_person/<int:person_id>/', del_person, name='delete_person'),
    path('form_fiz_l/<int:id>/', FizLFormView.as_view(), name='person_update'),
    path('form_fiz_l/', FizLFormView.as_view(), name='form_add_fiz_l'),
    path('form_marriage/', MarriageFormView.as_view(), name='form_add_marriage'),
    path('del_marriage/<int:marriage_id>/', del_marriage, name='delete_marriage'),
    path('form_marriage/<int:id>/', MarriageFormView.as_view(), name='marriage_update'),
    path('form_marriage_divorce/<int:id>/', MarriageFormDivorceView.as_view(), name='marriage_divorce'),
    path('form_property_1/', PropertyFormView.as_view(), name='form_add_property_1'),
    path('del_property/<int:property_id>/', del_property, name='delete_property'),
    path('form_property_1/<int:id>/', PropertyFormView.as_view(), name='property_update'),
    path('form_property_2_nm/', PropertyForm2nmView.as_view(), name='property_2_nm'),
    path('form_property_2_nm/<int:id>/', PropertyForm2nmView.as_view(), name='property_2_nm_update'),
    path('form_property_2_m/', PropertyForm2mView.as_view(), name='property_2_m'),
    path('form_property_2_m/<int:id>/', PropertyForm2mView.as_view(), name='property_2_m_update'),
    path('form_distribution/', DistributionFormView.as_view(), name='form_add_distribution'),
    path('del_distribution/<int:distribution_id>/', del_distribution, name='delete_distribution'),
    path('<int:property_id>/person_1', DivorceView.as_view(), name='common_to_person_1'),
    path('<int:property_id>/person_2', DivorceView.as_view(), name='common_to_person_2'),
    path('<int:property_id>/after_break_up', DivorceView.as_view(), name='common_to_private_after_break_up'),
    path('<int:property_id>/person_1', DivorceView.as_view(), name='convert_to_dolevaya'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
